# app/utils/common.py
"""Utility functions for the Reddit Scraper project."""
import os
import re
from datetime import datetime


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
