"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules

import os
import sys
from typing import Any, Callable, Dict

import openai
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry

from utils.openai import estimate_word_count, num_tokens_from_string

# Constants
SUMMARY_SIZE = 500
MAX_CHUNK_TOKEN_SIZE = 1000
MAX_TOKENS = 2049  # max number of token (note: text-curie-001 has a max of 2048)
GPT_MODEL = "text-curie-001"  # GPT-3 model to use
MAX_CHUNK_LENGTH = 2000

try:
    load_dotenv()
except FileNotFoundError:
    print("Could not find .env file. Please create one.")
    sys.exit(1)

openai.organization = os.environ.get("OPENAI_ORG_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Token bucket rate limiting parameters
RATE_LIMIT = 10  # max number of requests per minute
RATE_LIMIT_PERIOD = 60  # period in seconds


# Decorator for token bucket rate limiting
def token_bucket_rate_limit(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for token bucket rate limiting.
    """

    @sleep_and_retry
    @limits(calls=RATE_LIMIT, period=RATE_LIMIT_PERIOD)
    def rate_limited_func(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return rate_limited_func


def load_text_file(filename: str):
    """
    Load a text file from the same directory as this script.
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, filename)
    with open(file_path, "r", encoding="utf-8") as file:
        file_read_data = file.read()
    return file_read_data


def write_text_file(text: str, filename: str):
    """
    Write a text file from the same directory as this script.
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, filename)

    with open(file_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)

    return file_path


@token_bucket_rate_limit
def summarize_text(
    text: str, max_token_length: int, max_tokens: int = MAX_TOKENS
) -> str:
    """
    Summarize the prompt using GPT-3.
    """

    original_num_tokens = num_tokens_from_string(text)

    summary_size = max_token_length if max_token_length <= max_tokens else max_tokens

    def recursive_summarization(chunk_text: str, prefix_text: str = "") -> str:
        summary_string = (
            f"```{prefix_text}```\n\n"
            + "new text:\n\n```"
            # + f"{estimate_word_count(max_token_length)} words:\n"
            + chunk_text
            + "```\n\nsummarize then append to last text, write close to [replace] "
            " words, use extractive summarization if you have too much text, use"
            " abstractive summarization (no gibberish) if you don't have enough:\n\n```"
        )

        summary_string = summary_string.replace(
            "[replace]", str(estimate_word_count(summary_size))
        )

        response: Dict[str, Any] = openai.Completion.create(  # type: ignore
            model=GPT_MODEL,
            prompt=summary_string,
            frequency_penalty=0.5,
            max_tokens=MAX_TOKENS
            - num_tokens_from_string(summary_string),  # eg 4000-(len chunk+len string)
        )

        if len(response) == 0:
            print("response=", response)  # error
            return "Error: unable to generate response."

        response_text = response["choices"][0]["text"]
        return response_text

    chunks = [
        text[i : i + MAX_CHUNK_LENGTH] for i in range(0, len(text), MAX_CHUNK_LENGTH)
    ]
    result = ""
    summary = ""
    for chunk in chunks:
        print("chunk=", chunk)
        summary = recursive_summarization(chunk, summary)
        result += summary

    num_tokens = num_tokens_from_string(result)
    print("num_tokens=", num_tokens, "original_num_tokens=", original_num_tokens)

    if num_tokens > max_token_length:
        # iterate again, EXPENSIVE try again
        print("dividing prompt")
        return summarize_text(result, max_token_length)

    return result


def cleanup_summary(text: str, summary_size: int, max_tokens: int = MAX_TOKENS) -> str:
    """
    Cleanup the summary using GPT-3.

    Args:
        text (str): The text to summarize.
        summary_size (int): The desired summary size in tokens.
        max_tokens (int): The maximum number of tokens to use.
    """

    summary_size = summary_size if summary_size <= max_tokens else max_tokens

    cleanup_prompt = (
        "cleanup this machine generated summarization, notably "
        + "in the ligatures between passages, write close to [replace] words, use"
        " extractive summarization if you have too much text, use abstractive"
        " summarization if you don't have enough, no gibberish or bad"
        f" formatting:\n```{text}```"
    )

    cleanup_prompt = cleanup_prompt.replace(
        "[replace]", str(estimate_word_count(summary_size))
    )

    response: Dict[str, Any] = openai.Completion.create(  # type: ignore
        model="text-davinci-003",
        prompt=cleanup_prompt,
        best_of=3,
        max_tokens=max_tokens - num_tokens_from_string(cleanup_prompt),
    )
    if len(response) == 0:
        print("response error=", response)  # error
        return "Error: unable to generate response."

    response_text = response["choices"][0]["text"]
    print("response_text=", response_text)
    return response_text


print("go")
filetext = load_text_file("../inputs/HomeSummary.txt")
output = summarize_text(filetext, SUMMARY_SIZE)
output = cleanup_summary(output, SUMMARY_SIZE)  # perform a cleanup pass

path = write_text_file(output, "../outputs/recursive_summary_test_output.txt")
print("Output written to", path)