"""Utility functions for the Reddit Scraper project."""
import os
import re
from datetime import datetime
from typing import List

from services.openai_methods import estimate_word_count, num_tokens_from_string

HEADERS = {"User-Agent": "Mozilla/5.0"}


def generate_filename(title: str) -> str:
    """Generate a filename from the given title."""
    # Remove all special characters and spaces from the title
    filename = re.sub(r"[^\w\s]", "", title)
    # Replace all remaining spaces with underscores
    filename = filename.replace(" ", "_")
    # Shorten the filename if it is too long
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def get_timestamp() -> str:
    """Get a timestamp in the format YYYYMMDDHHMMSS."""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def save_output(title: str, output: str) -> str:
    """
    Save the output to a file in current working dir. The filename will
    be the generated from the title, santized with a timestamp appended to it.
    """
    # Get the current working directory
    cwd = os.getcwd()

    # Define the relative path to the output folder
    output_folder = "outputs"

    # Construct the full path to the output folder
    output_path = os.path.join(cwd, output_folder)

    # Create the output folder if it does not exist
    os.makedirs(output_path, exist_ok=True)

    # Create the output filename with a timestamp
    output_filename = f"{generate_filename(title)}_{get_timestamp()}.txt"

    # Construct the full path to the output file
    output_file_path = os.path.join(output_path, output_filename)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(output)

    return output_file_path


def replace_last_token_with_json(reddit_url: str) -> str:
    """
    Replace the last token in the Reddit URL with ".json".
    """
    tokens = reddit_url.rsplit("/", 1)
    new_url = tokens[0] + ".json"
    return new_url


def is_valid_reddit_url(url: str) -> bool:
    """
    Check if the URL is valid.
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
    Concatenate the bodies into an array of newline delimited strings that are
    < token_length tokens long
    """
    results: List[str] = []
    result = ""
    for line in contents.split("\n"):
        line = re.sub(r"\n+", "\n", line).strip()
        result += line[: estimate_word_count(1000)] + "\n"

        if num_tokens_from_string(result) > token_length:
            results.append(result)
            result = ""
    if result:
        results.append(result)
    return results
