"""OpenAI Utility functions for the Reddit Scraper project."""
import os
import sys
from typing import Any, Dict

import openai
import tiktoken
from dotenv import load_dotenv

from utils.logger import logger

GPT_MODEL = "text-davinci-002"  # GPT-3 model to use

try:
    load_dotenv()
except FileNotFoundError:
    logger.error("Could not find .env file. Please create one.")
    sys.exit(1)

openai.organization = os.environ.get("OPENAI_ORG_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")


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
    estimated_word_count = round(num_tokens * 0.56)

    return estimated_word_count


def complete_text(prompt: str, max_tokens: int) -> str:
    """
    Use OpenAI's GPT-3 model to complete text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.
        max_tokens (int, optional): The maximum number of tokens to generate in the
        response. Defaults to MAX_TOKENS - num_tokens_from_string(prompt).

    Returns:
        str: The completed text.
    """

    response: Dict[str, Any] = openai.Completion.create(  # type: ignore
        model=GPT_MODEL,
        prompt=prompt,
        temperature=0.9,
        max_tokens=max_tokens,
    )

    if len(response) == 0:
        logger.error("response=%s", response)  # error
        return "Error: unable to generate response."

    return response["choices"][0]["text"]
