"""Utility functions for the Reddit Scraper project."""
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, Generator, List, Tuple, Union

import requests

from utils.openai import estimate_word_count, num_tokens_from_string

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


def request_json_from_url(url: str) -> list[dict[str, Any]]:
    """
    Make a request to the given URL and return the JSON response.
    """
    json_data = {}
    try:
        with requests.get(url, headers=HEADERS, timeout=10) as response:
            response.raise_for_status()
            try:
                json_data = response.json()
            except json.decoder.JSONDecodeError as err:
                print(f"There was an error decoding the JSON response: {err}")

                sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"There was an error making the request: {err}")
        sys.exit(1)

    return json_data


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
    new_url = tokens[0] + "/.json"
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


def get_metadata_from_reddit_json(data: list[dict[str, Any]]) -> Tuple[str, str]:
    """
    Get the title and selftext from the reddit json data.
    """
    try:
        child_data = data[0]["data"]["children"][0]["data"]
        title = child_data["title"]
        selftext = child_data["selftext"]
    except (KeyError, IndexError) as exc:
        raise ValueError(
            "Invalid JSON data. Please check the Reddit URL and try again."
        ) from exc
    if title is None:
        raise ValueError("Title not found in Reddit thread data.")
    if selftext is None:
        raise ValueError("Selftext not found in Reddit thread data.")
    return title, selftext


def get_comment_bodies(
    data: Union[Dict[str, Any], List[Any], str], path: List[Union[str, int]]
) -> Generator[Tuple[str, str], None, Any]:
    """
    Recursively iterate through the data and yield the path and value of the 'body' key.
    """
    # If data is a dictionary, check if it has a 'body' key
    if isinstance(data, dict):
        if "body" in data:
            # If the dictionary has a 'body' key, yield the path and value of the 'body'
            path_str = "/".join([str(x) for x in path])
            yield (path_str, "[" + data["author"] + "] " + data["body"])
        # Iterate through the dictionary's key-value pairs
        for key, value in data.items():
            # Recursively call the function with the value and updated path
            yield from get_comment_bodies(value, path + [key])
    # If data is a list, iterate through the elements
    elif isinstance(data, list):
        for index, item in enumerate(data):
            # Recursively call the function with the element and updated path
            yield from get_comment_bodies(item, path + [repr(index)])


def group_bodies_into_chunks(
    contents: List[Tuple[str, str]], token_length: int
) -> List[str]:
    """
    Concatenate the bodies into an array of newline delimited strings that are
    < token_length tokens long
    """
    results: List[str] = []
    result = ""
    for body_tuple in contents:
        if body_tuple[1]:
            # replace one or more consecutive newline characters
            body_tuple = (body_tuple[0], re.sub(r"\n+", "\n", body_tuple[1]))
            result += body_tuple[1][: estimate_word_count(1000)] + "\n"

            if num_tokens_from_string(result) > token_length:
                results.append(result)
                result = ""
    if result:
        results.append(result)
    return results
