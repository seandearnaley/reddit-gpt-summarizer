"""data functions for Reddit Scraper project."""

import logging
import re
from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple

import praw  # type: ignore
from config import ConfigLoader
from data_types.summary import GenerateSettings, RedditData
from env import EnvVarsLoader
from log_tools import Logger
from services.openai_methods import (
    complete_text_chat,
    estimate_word_count,
    num_tokens_from_string,
)
from utils.common import group_bodies_into_chunks
from utils.streamlit_decorators import spinner_decorator

config = ConfigLoader.get_config()
env_vars = EnvVarsLoader.load_env()

app_logger = Logger.get_app_logger()
ProgressCallback = Optional[Callable[[int, int, str, str], None]]


@Logger.log
def summarize_summary(
    selftext: str,
    title: Optional[str] = None,
    max_tokens: int = config["MAX_BODY_TOKEN_SIZE"],
) -> str:
    """Summarize the response."""
    summary_string = (
        f"shorten this text to ~{max_tokens} GPT tokens through summarization:"
        f" {selftext}"
    )

    out_text = complete_text_chat(
        prompt=summary_string,
        max_tokens=max_tokens,
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
        comment.replies, key=lambda reply: reply.created_utc, reverse=True
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

        title: Optional[str] = submission.title
        selftext: Optional[str] = submission.selftext

        if not title:
            raise ValueError("No title found in JSON")

        comment_string = ""
        for comment in submission.comments:
            comment_string += get_comments(comment)

        return RedditData(
            title=title, selftext=selftext, subreddit=subreddit, comments=comment_string
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

        if not comments:
            comments = "No Comments"

        groups = group_bodies_into_chunks(comments, settings["chunk_token_length"])

        if len(groups) == 0:
            groups = ["No Comments"]

        if (selftext is None) or (len(selftext) == 0):
            selftext = "No selftext"

        groups = (
            group_bodies_into_chunks(comments, settings["chunk_token_length"])
            if len(groups) > 0
            else ["No Comments"]
        )

        # Check if selftext is too long, and summarize if necessary
        init_prompt = (
            summarize_summary(selftext, title)
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

        output = ""
        for i, summary in enumerate(summaries):
            prompt = prompts[i]
            output += f"============\nSUMMARY COUNT: {i}\n============\n"
            output += f"PROMPT: {prompt}\n\n{summary}\n===========================\n\n"

        return output

    except Exception as ex:  # pylint: disable=broad-except
        logger.error(f"Error generating summary data: {ex}")
        raise ex


@Logger.log
def generate_summaries(
    settings: GenerateSettings,
    groups: List[str],
    prompt: str,
    subreddit: str,
    progress_callback: ProgressCallback = None,
) -> Tuple[List[str], List[str]]:
    """Generate the summaries from the prompts."""

    prompts: List[str] = []
    summaries: List[str] = []
    total_groups = len(groups)
    system_role, query, max_tokens, model = (
        settings["system_role"],
        settings["query"],
        settings["max_token_length"],
        settings["selected_model"],
    )

    for i, comment_group in enumerate(groups):
        complete_prompt = (
            f"{query}\n\n"
            + "```"
            + f"Title: {summarize_summary(prompt) if i > 0 else prompt}\n\n"
            + f'<Comments subreddit="r/{subreddit}">\n{comment_group}\n</Comments>\n'
            + "```"
        )

        prompts.append(complete_prompt)

        summary = complete_text_chat(
            system_role=system_role,
            prompt=complete_prompt,
            max_tokens=max_tokens
            - num_tokens_from_string(complete_prompt)
            - num_tokens_from_string(system_role)
            - 4,  # figure out the 4
            model=model,
        )

        if progress_callback:
            progress = int(((i + 1) / total_groups) * 100)
            progress_callback(progress, i + 1, complete_prompt, summary)

        prompt = summary

        summaries.append(summary)
    return prompts, summaries
