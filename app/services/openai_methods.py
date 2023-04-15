"""OpenAI Utility functions for the Reddit Scraper project."""
import math
import re
from typing import Any, Dict, List

import openai
import tiktoken
from config import ConfigLoader
from env import EnvVarsLoader
from log_tools import Logger
from pyrate_limiter import Duration, Limiter, RequestRate
from utils.streamlit_decorators import error_to_streamlit

config = ConfigLoader.get_config()
app_logger = Logger.get_app_logger()
env_vars = EnvVarsLoader.load_env()

openai.organization = env_vars["OPENAI_ORG_ID"]
openai.api_key = env_vars["OPENAI_API_KEY"]

rate_limits = (RequestRate(10, Duration.MINUTE),)  # 10 requests a minute

# Create the rate limiter
# Pyrate Limiter instance
limiter = Limiter(*rate_limits)


def num_tokens_from_string(string: str, encoding_name: str = "gpt2") -> int:
    """
    Returns the number of tokens in a text string.
    https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def estimate_word_count(num_tokens: int) -> int:
    """
    Given the number of GPT-2 tokens, estimates the real word count.
    """
    # The average number of real words per token for GPT-2 is 0.56, according to OpenAI.
    # Multiply the number of tokens by this average to estimate the total number of real
    # words.
    return math.ceil(num_tokens * 0.56)


def validate_max_tokens(max_tokens: int) -> None:
    if max_tokens <= 0:
        raise ValueError("The input max_tokens must be a positive integer.")


@Logger.log
@error_to_streamlit
def complete_text(
    prompt: str,
    max_tokens: int,
    model: str = config["DEFAULT_GPT_MODEL"],
) -> str:
    """
    Use OpenAI's GPT-3 model to complete text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.
        max_tokens (int, optional): The maximum number of tokens to generate in the
        response. Defaults to MAX_TOKENS - num_tokens_from_string(prompt).
        org_id (str): The OpenAI organization ID.
        api_key (str): The OpenAI API key.
        model (str, optional): The OpenAI GPT-3 model to use. Defaults to
        DEFAULT_GPT_MODEL.

    Returns:
        str: The completed text.
    """

    app_logger.info("max_tokens=%s", max_tokens)
    validate_max_tokens(max_tokens)

    try:
        response: Dict[str, Any] = openai.Completion.create(  # type: ignore
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
        )
    except Exception as ex:  # pylint: disable=broad-except
        return f"Error: unable to generate response: {ex}"

    if len(response) == 0:
        return "Response length is 0"

    return response["choices"][0]["text"]  # completed_text


@Logger.log
@error_to_streamlit
def complete_text_chat(
    prompt: str,
    max_tokens: int,
    model: str = "gpt-3.5-turbo-0301",
    system_role: str = config["DEFAULT_SYSTEM_ROLE"],
) -> str:
    """
    Use OpenAI's ChatGPT to complete text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.
        max_tokens (int, optional): The maximum number of tokens to generate in the
        response. Defaults to MAX_TOKENS - num_tokens_from_string(prompt).
        org_id (str): The OpenAI organization ID.
        api_key (str): The OpenAI API key.
        model (str, optional): The OpenAI GPT-3 model to use. Defaults to
        'gpt-3.5-turbo-0301'.

    Returns:
        str: The completed text.
    """
    app_logger.info("max_tokens=%s", max_tokens)
    validate_max_tokens(max_tokens)

    try:
        limiter.ratelimit("complete_text_chat")
        response: Dict[str, Any] = openai.ChatCompletion.create(  # type: ignore
            model=model,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            frequency_penalty=0.7,
        )
    except Exception as ex:  # pylint: disable=broad-except
        return f"Error: unable to generate response: {ex}"

    if len(response) == 0:
        return "Response length is 0"
    return response["choices"][0]["message"]["content"]  # completed_text


def get_models() -> Dict[str, Any]:
    """
    Get a list of all available GPT-3 models.

    Args:
        org_id (str): The OpenAI organization ID.
        api_key (str): The OpenAI API key.

    Returns:
        dict: The response from OpenAI's Engine API.
    """
    response: Dict[str, Any] = openai.Engine.list()  # type: ignore
    return response["data"]


def group_bodies_into_chunks(contents: str, token_length: int) -> List[str]:
    """
    Concatenate the content lines into a list of newline-delimited strings
    that are less than token_length tokens long.
    """
    results: List[str] = []
    current_chunk = ""

    for line in contents.split("\n"):
        line = re.sub(r"\n+", "\n", line).strip()
        line = line[: estimate_word_count(1000)] + "\n"

        if num_tokens_from_string(current_chunk + line) > token_length:
            results.append(current_chunk)
            current_chunk = ""

        current_chunk += line

    if current_chunk:
        results.append(current_chunk)

    return results
