"""OpenAI Utility functions for the Reddit Scraper project."""
import math
import os
import sys
from typing import Any, Dict

import openai
import tiktoken
from dotenv import load_dotenv

from logger import app_logger

MAX_BODY_TOKEN_SIZE = 1000  # not in use yet
DEFAULT_GPT_MODEL = "text-davinci-002"  # GPT-3 model to use

try:
    load_dotenv()
except FileNotFoundError:
    app_logger.error("Could not find .env file. Please create one.")
    sys.exit(1)

openai.organization = os.getenv("OPENAI_ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")


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


def complete_text(prompt: str, max_tokens: int, model: str = DEFAULT_GPT_MODEL) -> str:
    """
    Use OpenAI's GPT-3 model to complete text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.
        max_tokens (int, optional): The maximum number of tokens to generate in the
        response. Defaults to MAX_TOKENS - num_tokens_from_string(prompt).

    Returns:
        str: The completed text.
    """

    if max_tokens <= 0:
        raise ValueError("The input max_tokens must be a positive integer.")

    response: Dict[str, Any] = openai.Completion.create(  # type: ignore
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
    )

    if len(response) == 0:
        app_logger.error("response=%s", response)  # error
        return "Error: unable to generate response."

    return response["choices"][0]["text"]  # completed_text


def summarize_body(body: str, max_length: int = MAX_BODY_TOKEN_SIZE) -> str:
    """
    Summarizes a body of text to be at most max_length tokens long.
    """
    if num_tokens_from_string(body) <= max_length:
        return body

    summary_string = f"summarize this text to under {max_length} GPT-2 tokens:\n" + body

    return complete_text(summary_string, num_tokens_from_string(summary_string))


def get_models() -> Dict[str, Any]:
    """Get a list of all available GPT-3 models."""
    response: Dict[str, Any] = openai.Engine.list()  # type: ignore
    return response["data"]
