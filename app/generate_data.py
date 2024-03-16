"""data functions for Reddit Scraper project."""

import logging
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional

import praw  # type: ignore
from config import ConfigVars
from data_types.summary import GenerateSettings, RedditData
from env import EnvVarsLoader
from llm_handler import complete_text
from log_tools import Logger
from utils.llm_utils import (
    estimate_word_count,
    group_bodies_into_chunks,
    num_tokens_from_string,
)
from utils.streamlit_decorators import spinner_decorator

config = ConfigVars()
env_vars = EnvVarsLoader.load_env()

app_logger = Logger.get_app_logger()
ProgressCallback = Optional[Callable[[int, int, str, str], None]]


@Logger.log
def summarize_summary(
    selftext: str,
    settings: GenerateSettings,
    title: str | None = None,
    max_tokens: int = config.MAX_BODY_TOKEN_SIZE,
) -> str:
    """Summarize the response."""

    summary_string = (
        f"shorten this text to ~{max_tokens} GPT tokens through summarization:"
        f" {selftext}"
    )

    out_text = complete_text(
        prompt=summary_string, max_tokens=max_tokens, settings=settings,
    )

    if title is None:
        return out_text
    return f"{title}\n{out_text}"


def format_date(timestamp: float) -> str:
    """Format a timestamp into a human-readable date."""
    date: datetime = datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%b-%d %H:%M")


def get_comments(comment: Any, level: int = 0) -> str:
    """Get the comments from a Reddit thread."""
    result = ""

    author_name = comment.author.name if comment.author else "[deleted]"
    created_date = format_date(comment.created_utc)

    result += f"{created_date} [{author_name}] {comment.body}\n"

    for reply in sorted(
        comment.replies, key=lambda reply: reply.created_utc, reverse=True,
    ):
        result += "    " * level
        result += "> " + get_comments(reply, level + 1)

    return result


@spinner_decorator("Getting Reddit w/ PRAW")
def get_reddit_praw(
    json_url: str,
    logger: logging.Logger,
) -> RedditData:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        # Get the subreddit and metadata from the JSON
        match = re.search(r"/r/(\w+)/", json_url)
        if match:
            subreddit = match.group(1)
        else:
            raise ValueError("No subreddit found in URL")

        reddit = praw.Reddit(
            client_id=env_vars["REDDIT_CLIENT_ID"],
            client_secret=env_vars["REDDIT_CLIENT_SECRET"],
            password=env_vars["REDDIT_PASSWORD"],
            user_agent=env_vars["REDDIT_USER_AGENT"],
            username=env_vars["REDDIT_USERNAME"],
        )

        submission: Any = reddit.submission(url=json_url)  # type: ignore
        submission.comment_sort = "top"  # sort comments by score (upvotes - downvotes)
        submission.comments.replace_more(limit=None)

        title: str | None = submission.title
        selftext: str | None = submission.selftext

        if not title:
            raise ValueError("No title found in JSON")

        comment_string = ""
        for comment in submission.comments:
            comment_string += get_comments(comment)

        return RedditData(
            title=title, selftext=selftext, subreddit=subreddit, comments=comment_string,
        )

    except Exception as ex:  # pylint: disable=broad-except
        logger.error(f"Error getting reddit meta data: {ex}")
        raise ex


@spinner_decorator("Generating Summary Data")
def generate_summary_data(
    settings: GenerateSettings,
    reddit_data: RedditData,
    logger: logging.Logger,
    progress_callback: ProgressCallback = None,
) -> str:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        title, selftext, subreddit, comments = (
            reddit_data["title"],
            reddit_data["selftext"],
            reddit_data["subreddit"],
            reddit_data["comments"],
        )

        comments = comments or "No Comments"
        groups = group_bodies_into_chunks(comments, settings["chunk_token_length"]) or [
            "No Comments",
        ]
        selftext = selftext or "No selftext"

        init_prompt = (
            summarize_summary(selftext, settings, title)
            if len(selftext) > estimate_word_count(settings["max_token_length"])
            else f"{title}\n{selftext}"
        )

        prompts, summaries = generate_summaries(
            settings=settings,
            groups=groups[: settings["max_number_of_summaries"]],
            prompt=init_prompt,
            subreddit=subreddit,
            progress_callback=progress_callback,
        )

        output = "\n".join(
            f"============\nSUMMARY COUNT: {i}\n"
            f"============\nPROMPT: {prompt}\n\n"
            f"{summary}\n===========================\n"
            for i, (prompt, summary) in enumerate(zip(prompts, summaries, strict=False))
        )

        return output

    except Exception as ex:
        logger.error(f"Error generating summary data: {ex}")
        raise


@Logger.log
def generate_complete_prompt(
    comment_group: str, title: str, settings: GenerateSettings, subreddit: str,
) -> str:
    """Generate the complete prompt."""
    return (
        f"{settings['query']}\n\n"
        f"```Title: {title}\n\n"
        f"<Comments subreddit='r/{subreddit}'>\n"
        f"{comment_group}\n</Comments>\n```"
    )


@Logger.log
def adjust_prompt_length(
    comment_group: str,
    title: str,
    settings: GenerateSettings,
    max_context_length: int,
    subreddit: str,
) -> str:
    """Ensure the prompt does not exceed the max_context_length."""
    complete_prompt = generate_complete_prompt(
        comment_group, title, settings, subreddit,
    )
    prompt_token_count = num_tokens_from_string(
        complete_prompt, settings["selected_model_type"],
    )
    while prompt_token_count > max_context_length and comment_group:
        comment_group = comment_group[:-1]
        complete_prompt = generate_complete_prompt(
            comment_group, title, settings, subreddit,
        )
        prompt_token_count = num_tokens_from_string(
            complete_prompt, settings["selected_model_type"],
        )
    return complete_prompt


@Logger.log
def generate_summaries(
    settings: GenerateSettings,
    groups: list[str],
    prompt: str,
    subreddit: str,
    progress_callback: ProgressCallback = None,
) -> tuple[list[str], list[str]]:
    """Generate the summaries from the prompts."""

    total_groups = len(groups)
    max_context_length = settings["max_context_length"]

    summaries = [
        generate_summary(
            i,
            comment_group,
            prompt,
            settings,
            max_context_length,
            subreddit,
            progress_callback,
            total_groups,
        )
        for i, comment_group in enumerate(groups)
    ]

    prompts = [summary[0] for summary in summaries]
    summaries = [summary[1] for summary in summaries]

    return prompts, summaries


@Logger.log
def generate_summary(
    i: int,
    comment_group: str,
    prompt: str,
    settings: GenerateSettings,
    max_context_length: int,
    subreddit: str = "",
    progress_callback: ProgressCallback = None,
    total_groups: int = 1,
) -> tuple[str, str]:
    """Generate a single summary."""

    title = summarize_summary(prompt, settings) if i > 0 else prompt

    complete_prompt = adjust_prompt_length(
        comment_group, title, settings, max_context_length, subreddit,
    )

    max_tokens = min(
        max_context_length
        - num_tokens_from_string(complete_prompt, settings["selected_model_type"]),
        settings["max_token_length"],
    )
    summary = complete_text(
        prompt=complete_prompt,
        max_tokens=max_tokens,
        settings=settings,
    )

    if progress_callback:
        progress = int(((i + 1) / total_groups) * 100)
        progress_callback(progress, i + 1, complete_prompt, summary)

    return complete_prompt, summary
