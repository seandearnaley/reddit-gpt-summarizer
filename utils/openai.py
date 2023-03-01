"""OpenAI Utility functions for the Reddit Scraper project."""
import math
from typing import Any, Dict

import openai
import tiktoken

from log_tools import app_logger, log
from utils.streamlit_decorators import error_to_streamlit

DEFAULT_GPT_MODEL = "text-davinci-002"  # GPT-3 model to use


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
    estimated_word_count = math.ceil(num_tokens * 0.56)

    return estimated_word_count


@log
@error_to_streamlit
def complete_text(
    prompt: str,
    max_tokens: int,
    org_id: str,
    api_key: str,
    model: str = DEFAULT_GPT_MODEL,
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
    openai.organization = org_id
    openai.api_key = api_key
    app_logger.info("max_tokens=%s", max_tokens)
    if max_tokens <= 0:
        raise ValueError("The input max_tokens must be a positive integer.")

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


@log
@error_to_streamlit
def complete_text_chat(
    prompt: str,
    max_tokens: int,
    org_id: str,
    api_key: str,
    model: str = "gpt-3.5-turbo-0301",
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
        DEFAULT_GPT_MODEL.

    Returns:
        str: The completed text.
    """
    openai.organization = org_id
    openai.api_key = api_key
    app_logger.info("max_tokens=%s", max_tokens)
    if max_tokens <= 0:
        raise ValueError("The input max_tokens must be a positive integer.")

    try:
        response: Dict[str, Any] = openai.ChatCompletion.create(  # type: ignore
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional writer."},
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


def get_models(org_id: str, api_key: str) -> Dict[str, Any]:
    """
    Get a list of all available GPT-3 models.

    Args:
        org_id (str): The OpenAI organization ID.
        api_key (str): The OpenAI API key.

    Returns:
        dict: The response from OpenAI's Engine API.
    """
    openai.organization = org_id
    openai.api_key = api_key

    response: Dict[str, Any] = openai.Engine.list()  # type: ignore
    return response["data"]
