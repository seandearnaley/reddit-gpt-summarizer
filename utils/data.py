"""data functions for Reddit Scraper project."""


import logging
from typing import List, Optional, TypedDict

from config import get_config
from log_tools import log
from utils.common import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
    request_json_from_url,
)
from utils.openai import complete_text, estimate_word_count, num_tokens_from_string

config = get_config()


class SummaryData(TypedDict):
    """Summary data for the OpenAI API."""

    title: str
    selftext: str
    output: str
    prompts: List[str]
    summaries: List[str]
    groups: List[str]


@log
def generate_prompts(
    title: str, selftext: str, groups: List[str], query: str, subreddit: str
) -> List[str]:
    """Generate the prompts for the OpenAI API."""
    prompts: List[str] = []
    for comment_group in groups:
        prompt = (
            f"{query}\n\n```Title: "
            f"{title}\n{selftext[: estimate_word_count(500)]}\n\nr/{subreddit} on "
            f"REDDIT\nCOMMENTS BEGIN\n{comment_group}\nCOMMENTS END\n```\nTitle: "
        )
        prompts.append(prompt)
    return prompts


@log
def summarize_body(
    body: str,
    org_id: str,
    api_key: str,
    max_length: int = config["MAX_BODY_TOKEN_SIZE"],
) -> str:
    """
    Summarizes a body of text to be at most max_length tokens long.
    """
    if num_tokens_from_string(body) <= max_length:
        return body

    summary_string = f"summarize this text to under {max_length} GPT-2 tokens:\n" + body

    return complete_text(
        summary_string,
        num_tokens_from_string(summary_string),
        org_id,
        api_key,
    )


@log
def generate_completions(
    prompts: List[str],
    max_token_length: int,
    model: str,
    org_id: str,
    api_key: str,
) -> List[str]:
    """Generate the summaries from the prompts."""
    summaries: List[str] = []
    for prompt in prompts:
        summary = complete_text(
            prompt,
            max_token_length - num_tokens_from_string(prompt),
            org_id,
            api_key,
            model=model,
        )
        summaries.append(summary)
    return summaries


@log
def generate_summary_data(
    query: str,
    chunk_token_length: int,
    number_of_summaries: int,
    max_token_length: int,
    json_url: str,
    selected_model: str,
    org_id: str,
    api_key: str,
    logger: logging.Logger,
    # request_json_func = request_json_from_url,
    # complete_text_func=complete_text,
) -> Optional[SummaryData]:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        reddit_json = request_json_from_url(json_url, logger)
        if not reddit_json:
            raise ValueError("No JSON returned from URL")

        title, selftext = get_metadata_from_reddit_json(reddit_json)
        contents = list(get_comment_bodies(reddit_json, []))
        groups = group_bodies_into_chunks(contents, chunk_token_length)
        groups.insert(
            0, groups[0]
        )  # insert twice to get same comments in 2 top summaries

        logger.info("Generating Prompts")
        prompts = generate_prompts(
            title, selftext, groups[:number_of_summaries], query, config["SUBREDDIT"]
        )

        logger.info("Generating Completions")
        summaries = generate_completions(
            prompts, max_token_length, selected_model, org_id, api_key
        )

        output = ""
        for i, summary in enumerate(summaries):
            prompt = prompts[i]
            output += f"============\nSUMMARY COUNT: {i}\n============\n"
            output += f"PROMPT: {prompt}\n\n{summary}\n===========================\n\n"

        return {
            "title": title,
            "selftext": selftext,
            "output": output,
            "prompts": prompts,
            "summaries": summaries,
            "groups": groups,
        }
    except Exception as ex:  # pylint: disable=broad-except
        logger.error(f"Error generating summary data: {ex}")
        return None
