"""data functions for Reddit Scraper project."""


import logging
from typing import List, Optional, Tuple, TypedDict

from config import get_config
from log_tools import log
from utils.common import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
    request_json_from_url,
)
from utils.openai import complete_text_chat, num_tokens_from_string
from utils.streamlit_decorators import spinner_decorator

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
def summarize_body(
    body: str,
    org_id: str,
    api_key: str,
    max_tokens: int = config["MAX_BODY_TOKEN_SIZE"],
) -> str:
    """
    Summarizes a body of text to be at most max_length tokens long.
    """
    summary_string = (
        f"summarize this text, don't go over {max_tokens} GPT-2 tokens:\n" + body
    )

    return complete_text_chat(
        prompt=summary_string,
        max_tokens=max_tokens,
        org_id=org_id,
        api_key=api_key,
    )


@log
def generate_summaries(
    query: str,
    groups: List[str],
    max_token_length: int,
    model: str,
    org_id: str,
    api_key: str,
    prompt: str,
    subreddit: str,
) -> Tuple[List[str], List[str]]:
    """Generate the summaries from the prompts."""
    prompts: List[str] = []
    summaries: List[str] = []
    for comment_group in groups:
        complete_prompt = (
            f"{query}\n\n```"
            + f"Title: {summarize_summary(prompt, org_id, api_key)}\n\n"
            + f"\n\nr/{subreddit} on REDDIT\nCOMMENTS BEGIN\n{comment_group}\n"
            + "COMMENTS END\n```"
        )

        prompts.append(complete_prompt)

        summary = complete_text_chat(
            prompt=complete_prompt,
            max_tokens=max_token_length - num_tokens_from_string(complete_prompt),
            org_id=org_id,
            api_key=api_key,
            model=model,
        )
        prompt = summary

        summaries.append(summary)
    return prompts, summaries


def summarize_summary(
    selftext: str, org_id: str, api_key: str, title: Optional[str] = None
) -> str:
    """Summarize the response."""
    # out_text = selftext[: estimate_word_count(500)]
    out_text = summarize_body(selftext, org_id, api_key)
    print(org_id, api_key)
    if title is None:
        return out_text
    return f"{title}\n{out_text}"


@log
@spinner_decorator("Generating Summary Data")
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
    subreddit: str,
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

        logger.info("Generating Completions")

        # start this will wrapped in new lines
        init_prompt = summarize_summary(selftext, org_id, api_key, title)

        prompts, summaries = generate_summaries(
            query,
            groups[:number_of_summaries],
            max_token_length,
            selected_model,
            org_id,
            api_key,
            init_prompt,
            subreddit,
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
