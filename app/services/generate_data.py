"""data functions for Reddit Scraper project."""

import logging
import re
from typing import Callable, List, Optional, Tuple

from config import ConfigLoader
from data_types.summary import GenerateSettings, RedditMeta
from log_tools import Logger
from services.openai_methods import (
    complete_text_chat,
    estimate_word_count,
    num_tokens_from_string,
)
from utils.common import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
    request_json_from_url,
)
from utils.streamlit_decorators import spinner_decorator

config = ConfigLoader.get_config()

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


@spinner_decorator("Getting Reddit Meta")
def get_reddit_meta(
    json_url: str,
    logger: logging.Logger,
) -> RedditMeta:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        # Request the JSON from the URL
        reddit_json = request_json_from_url(json_url)
        if not reddit_json:
            raise ValueError("No JSON")

        # Get the subreddit and metadata from the JSON
        match = re.search(r"/r/(\w+)/", json_url)
        if match:
            subreddit = match.group(1)
        else:
            raise ValueError("No subreddit found in URL")

        title, selftext = get_metadata_from_reddit_json(reddit_json)

        return RedditMeta(
            title=title, selftext=selftext, subreddit=subreddit, reddit_json=reddit_json
        )

    except Exception as ex:  # pylint: disable=broad-except
        logger.error(f"Error getting reddit meta data: {ex}")
        raise ex


@spinner_decorator("Generating Summary Data")
def generate_summary_data(
    settings: GenerateSettings,
    reddit_meta: RedditMeta,
    logger: logging.Logger,
    progress_callback: ProgressCallback = None,
) -> str:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        title, selftext, subreddit, reddit_json = (
            reddit_meta["title"],
            reddit_meta["selftext"],
            reddit_meta["subreddit"],
            reddit_meta["reddit_json"],
        )

        # Get the comment bodies from the JSON and group them into chunks
        contents = list(get_comment_bodies(reddit_json, []))

        groups = group_bodies_into_chunks(contents, settings["chunk_token_length"])

        if len(groups) == 0:
            groups = ["No Comments"]

        groups = (
            group_bodies_into_chunks(contents, settings["chunk_token_length"])
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
            + f"Title: {summarize_summary(prompt)}\n\n"
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
