# app/utils/common.py
"""Utility functions for the Reddit Scraper project."""
import os
import re
from datetime import datetime
from typing import List

from services.openai_methods import estimate_word_count, num_tokens_from_string


def generate_filename(title: str) -> str:
    """Generate a sanitized filename from the given title."""
    filename = re.sub(r"[^\w\s]", "", title)
    filename = filename.replace(" ", "_")
    return filename[:100]


def get_timestamp() -> str:
    """Get a timestamp in the format YYYYMMDDHHMMSS."""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def save_output(title: str, output: str) -> str:
    """
    Save the output to a file in the 'outputs' directory.
    The filename is generated from the sanitized title with a timestamp appended.
    """
    output_folder = "outputs"
    output_path = os.path.join(os.getcwd(), output_folder)
    os.makedirs(output_path, exist_ok=True)

    output_filename = f"{generate_filename(title)}_{get_timestamp()}.txt"
    output_file_path = os.path.join(output_path, output_filename)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(output)

    return output_file_path


def replace_last_token_with_json(reddit_url: str) -> str:
    """Replace the last token in the Reddit URL with '.json'."""
    tokens = reddit_url.rsplit("/", 1)
    return f"{tokens[0]}.json"


def is_valid_reddit_url(url: str) -> bool:
    """
    Check if the URL is a valid Reddit URL.
    """
    pattern = re.compile(
        r"^"  # Start of the string
        r"(http(s)?:\/\/)?"  # Optional "http://" or "https://"
        r"(www\.)?"  # Optional "www."
        r"reddit\.com\/"  # "reddit.com/"
        r"([a-zA-Z0-9-_]+\/)+"  # 1 or more letters, numbers, -'s, or _ followed by "/"
        r"[a-zA-Z0-9-_]+"  # 1 or more letters, numbers, -'s, or _'s
        r"\/$"  # End of the string
    )
    return bool(pattern.match(url))


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
