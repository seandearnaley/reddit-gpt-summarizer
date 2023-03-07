"""data functions for Reddit Scraper project."""


import logging
from typing import Callable, List, Optional, Tuple

from config import get_config
from data_types.summary import GenerateSettings, SummaryData
from log_tools import log
from services.openai_methods import complete_text_chat, num_tokens_from_string
from utils.common import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
    request_json_from_url,
)
from utils.streamlit_decorators import spinner_decorator

config = get_config()

ProgressCallback = Optional[Callable[[int], None]]


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
    settings: GenerateSettings,
    groups: List[str],
    org_id: str,
    api_key: str,
    prompt: str,
    subreddit: str,
    progress_callback: ProgressCallback = None,
) -> Tuple[List[str], List[str]]:
    """Generate the summaries from the prompts."""
    prompts: List[str] = []
    summaries: List[str] = []
    total_groups = len(groups)
    for i, comment_group in enumerate(groups):
        complete_prompt = (
            f"{settings['query']}\n\n```"
            + f"Title: {summarize_summary(prompt, org_id, api_key)}\n\n"
            + f"\n\nr/{subreddit} on REDDIT\nCOMMENTS BEGIN\n{comment_group}\n"
            + "COMMENTS END\n```"
        )

        prompts.append(complete_prompt)

        summary = complete_text_chat(
            prompt=complete_prompt,
            max_tokens=settings["max_token_length"]
            - num_tokens_from_string(complete_prompt),
            org_id=org_id,
            api_key=api_key,
            model=settings["selected_model"],
        )

        if progress_callback:
            progress = int(((i + 1) / total_groups) * 100)
            progress_callback(progress)

        prompt = summary

        summaries.append(summary)
    return prompts, summaries


@log
def summarize_summary(
    selftext: str, org_id: str, api_key: str, title: Optional[str] = None
) -> str:
    """Summarize the response."""
    out_text = summarize_body(selftext, org_id, api_key)
    if title is None:
        return out_text
    return f"{title}\n{out_text}"


@log
@spinner_decorator("Generating Summary Data")
def generate_summary_data(
    settings: GenerateSettings,
    json_url: str,
    org_id: str,
    api_key: str,
    logger: logging.Logger,
    progress_callback: ProgressCallback = None,
    # request_json_func = request_json_from_url, add inections
    # complete_text_func=complete_text, add injections
) -> Optional[SummaryData]:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        reddit_json = request_json_from_url(json_url)
        subreddit = json_url.split("/", maxsplit=1)[0]
        if not reddit_json:
            raise ValueError("No JSON")

        title, selftext = get_metadata_from_reddit_json(reddit_json)
        contents = list(get_comment_bodies(reddit_json, []))
        groups = group_bodies_into_chunks(contents, settings["chunk_token_length"])
        groups.insert(
            0, groups[0]
        )  # hacky insert twice to get same comments in 2 top summaries

        logger.info("Generating Completions")

        # # summarize if length of selftext > 500 characters
        # init_prompt = (
        #     summarize_summary(selftext, org_id, api_key, title)
        #     if len(selftext) > 500
        #     else selftext
        # )

        init_prompt = summarize_summary(selftext, org_id, api_key, title)

        prompts, summaries = generate_summaries(
            settings=settings,
            groups=groups[: settings["max_number_of_summaries"]],
            org_id=org_id,
            api_key=api_key,
            prompt=init_prompt,
            subreddit=subreddit,
            progress_callback=progress_callback,
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
