"""Utility functions for the Reddit Scraper project."""
import re
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any
import tiktoken
import requests

# Headers to mimic a browser visit
headers = {"User-Agent": "Mozilla/5.0"}


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Returns the number of tokens in a text string.
    https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def generate_filename(title) -> str:
    """Generate a filename from the given title."""
    # Remove all special characters and spaces from the title
    filename = re.sub(r"[^\w\s]", "", title)
    # Replace all remaining spaces with underscores
    filename = filename.replace(" ", "_")
    # Shorten the filename if it is too long
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def request_json_from_url(url: str) -> Dict[str, Any]:
    """
    Make a request to the given URL and return the JSON response.
    """
    try:
        with requests.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            try:
                data = response.json()
            except json.decoder.JSONDecodeError as err:
                print(f"There was an error decoding the JSON response: {err}")
                sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"There was an error making the request: {err}")
        sys.exit(1)

    return data


def save_output(title: str, output: str) -> str:
    """
    Save the output to a file in current working dir. The filename will be the title
    with a timestamp appended to it.
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
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"{generate_filename(title)}_{timestamp}.txt"

    # Construct the full path to the output file
    output_file_path = os.path.join(output_path, output_filename)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(output)

    return output_file_path
