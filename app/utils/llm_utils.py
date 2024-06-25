"""Utility functions for the Large Language Models."""

import math
import re

import tiktoken
from anthropic import Anthropic


def group_bodies_into_chunks(contents: str, token_length: int) -> list[str]:
    """
    Concatenate the content lines into a list of newline-delimited strings
    that are less than token_length tokens long.
    """
    results: list[str] = []
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


def anthropic_sync_count_tokens(text: str) -> int:
    """Count the number of tokens in a text string using the Anthropic API."""
    client = Anthropic()
    number_of_tokens = client.count_tokens(text)
    return number_of_tokens


def num_tokens_from_string(string: str) -> int:
    """
    Returns the number of tokens in a text string.
    NOTE: openAI and Anthropics have different token counting mechanisms.
    https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    """

    num_tokens = len(tiktoken.get_encoding("gpt2").encode(string))
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
    """
    Validate the max_tokens argument, raising a ValueError if it is not valid.
    """
    if max_tokens <= 0:
        raise ValueError("The input max_tokens must be a positive integer.")
