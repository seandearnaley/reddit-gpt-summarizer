import requests
from transformers import GPT2Tokenizer
from bs4 import BeautifulSoup
import re
import json

# Set up the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Headers to mimic a browser visit
headers = {"User-Agent": "Mozilla/5.0"}


def get_token_length(text):
    # https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    tokens = tokenizer.tokenize(text)
    return len(tokens)


def download_parse_reddit_thread(url):
    # Make a request to the URL and retrieve the HTML content
    response = requests.get(url, headers=headers)
    html_content = response.text

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")

    return soup.get_text("|", strip=True).replace("Reply|Share|Report|Save|Follow", "")


def generate_filename(title) -> str:
    # Remove all special characters and spaces from the title
    filename = re.sub(r"[^\w\s]", "", title)
    # Replace all remaining spaces with underscores
    filename = filename.replace(" ", "_")
    # Shorten the filename if it is too long
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def request_json_from_url(url: str) -> dict:
    # Make a request to the URL and retrieve the JSON content
    try:
        with requests.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
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
