"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules
from datetime import datetime
import os
import re
from pathlib import Path
from typing import Generator, Tuple, List, Union
import openai
from dotenv import load_dotenv
from utils import get_token_length, generate_filename, request_json_from_url

load_dotenv()

# number of tokens to summarize to
MAX_CHUNK_SIZE = 2600
GROUP_LIMIT = 1

# OpenAI Constants
MODEL_MAX_TOKENS = 4000
GPT_MODEL = "text-davinci-003"

# reddit URL/ make sure to add .json to the end of the URL
REDDIT_URL = (
    "https://www.reddit.com/r/"
    "LeopardsAteMyFace/comments/101ykfm/bow_before_the_genius_god_of_business.json"
)

PROMPT_STRING = (
    "Building upon this, professionally edit the article, use any additional relevant information"
    + " provided in the comment thread below, revise, enhance and make it engaging. Don't include"
    + " code or commands and optimize for facts as well as readability, share sentiment but"
    + " remain inpartial."
)

openai.organization = os.environ.get("OPENAI_ORG_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")


def get_metadata_from_reddit_json(data: dict) -> Tuple[str, str]:
    """
    Get the title and selftext from the reddit json data.
    """
    child_data = data[0]["data"]["children"][0]["data"]
    if "title" not in child_data:
        raise ValueError("Title not found in child data")
    if "selftext" not in child_data:
        raise ValueError("Selftext not found in child data")
    return (child_data["title"], child_data["selftext"])


def get_body_contents(
    data: Union[List[Union[dict, str]], dict], path: List[str]
) -> Generator[Tuple[str, str], int, None]:
    """
    Generator function that yields tuples of the form (path, body_content) for
    all dictionaries in the input data with a key of 'body'.
    """
    # If data is a dictionary, check if it has a 'body' key
    if isinstance(data, dict):
        if "body" in data:
            # If the dictionary has a 'body' key, yield the path and value of the 'body' key
            path_str = "/".join([str(x) for x in path])
            yield (path_str, data["body"])
        # Iterate through the dictionary's key-value pairs
        for key, value in data.items():
            # Recursively call the function with the value and updated path
            yield from get_body_contents(value, path + [key])
    # If data is a list, iterate through the elements
    elif isinstance(data, list):
        for index, item in enumerate(data):
            # Recursively call the function with the element and updated path
            yield from get_body_contents(item, path + [index])


def concatenate_bodies(contents: List[Tuple[str, str]]) -> List[str]:
    """
    Concatenate the bodies into an array of newline delimited strings that are
    ~MAX_CHUNK_SIZE tokens long
    """
    results = []
    result = ""
    for body_tuple in contents:
        if body_tuple[1]:
            # replace one or more consecutive newline characters
            body_tuple = (body_tuple[0], re.sub(r"\n+", "\n", body_tuple[1]))
            result += body_tuple[1] + "\n"
            if get_token_length(result) > MAX_CHUNK_SIZE:
                results.append(result)
                result = ""
    if result:
        results.append(result)
    return results


def complete_chunk(prompt: str) -> str:
    """
    Use OpenAI's GPT-3 model to complete a chunk of text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.

    Returns:
        str: The completed chunk of text.
    """
    print("prompt=" + prompt)
    print("token length: " + str(get_token_length(prompt)))
    response = openai.Completion.create(
        model=GPT_MODEL,
        prompt=prompt,
        temperature=0.9,
        max_tokens=MODEL_MAX_TOKENS - get_token_length(prompt),
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0.6
    )
    # print(response.choices[0].text)
    return response.choices[0].text


def main():
    """
    Main function.
    """
    data = request_json_from_url(REDDIT_URL)

    # write raw json output to file
    Path("output.json").write_text(str(data), encoding="utf-8")

    # get an array of body contents
    contents = get_body_contents(data, [])

    # concatenate the bodies into an array of newline delimited strings
    groups = concatenate_bodies(contents)

    # Get the current working directory
    cwd = os.getcwd()

    # Define the relative path to the output folder
    output_folder = "outputs"

    # Construct the full path to the output folder
    output_path = os.path.join(cwd, output_folder)

    # Create the output folder if it does not exist
    os.makedirs(output_path, exist_ok=True)

    # Get the title and selftext from the reddit thread JSON
    title, selftext = get_metadata_from_reddit_json(data)

    # Create the output filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"{generate_filename(title)}_{timestamp}.txt"

    # Construct the full path to the output file
    output_file_path = os.path.join(output_path, output_filename)

    # initialize the prefix with the title and selftext of the reddit thread JSON
    prefix = f"Title: {title}\n{selftext}"

    # Use f-strings for string formatting
    output = f"START\n\n{PROMPT_STRING}\n\n"

    # Use enumerate to get the index and the group in each iteration
    for i, group in enumerate(groups[:GROUP_LIMIT]):
        # Use triple quotes to create a multi-line string
        prompt = f"""{prefix}

{PROMPT_STRING}

COMMENTS BEGIN
{group}
COMMENTS END

Title:"""
        summary = complete_chunk(prompt)
        prefix = f"{title}\n\n{summary}\nEND"
        # Use format method to insert values into a string
        output += f"\n\n============\nSUMMARY COUNT: {i}\n============\n\n"
        output += summary

    # Use the Path.write_text method to write to the output file
    Path(output_file_path).write_text(output, encoding="utf-8")

    print(output)


if __name__ == "__main__":
    main()
