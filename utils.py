"""Utility functions for the Reddit Scraper project."""
import re
import json
import requests
from typing import Union
from transformers import GPT2Tokenizer
from bs4 import BeautifulSoup


# Set up the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Headers to mimic a browser visit
headers = {"User-Agent": "Mozilla/5.0"}


def get_token_length(text):
    """
    Get the number of tokens in the given text.
    https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    """
    tokens = tokenizer.tokenize(text)
    return len(tokens)


def download_parse_reddit_thread(url):
    """
    Download the HTML content of the reddit thread and parse it using Beautiful Soup.
    """
    response = requests.get(url, headers=headers, timeout=10)
    html_content = response.text

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")

    return soup.get_text("|", strip=True).replace(
        "Reply|Share|Report|Save|Follow", ""
    )


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


def request_json_from_url(url: str) -> Union[dict, None]:
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
                return
    except requests.exceptions.RequestException as err:
        print(f"There was an error making the request: {err}")
        return

    return data
