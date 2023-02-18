"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules

import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

import openai
from dotenv import load_dotenv

from reddit_gpt_summarizer.utils import (
    estimate_word_count,
    num_tokens_from_string,
    request_json_from_url,
    save_output,
)

try:
    load_dotenv()
except FileNotFoundError:
    print("Could not find .env file. Please create one.")
    sys.exit(1)

# Constants
MAX_CHUNK_TOKEN_SIZE = 2000
MAX_BODY_TOKEN_SIZE = 1000
MAX_NUMBER_OF_SUMMARIES = 3
MAX_TOKENS = 4000

GPT_MODEL = "text-davinci-003"
THREAD_ID = "webdev/comments/8sumel/free_web_development_tutorials_for_those_who_are"
REDDIT_URL = f"https://www.reddit.com/r/{THREAD_ID}.json"
SUBREDDIT = THREAD_ID.split("/", maxsplit=1)[0]

INSTRUCTION_TEXT = (
    f"(Todays Date: {datetime.now().strftime('%Y-%b-%d')}) Revise and improve the "
    "article by incorporating relevant information from the comments. Ensure the "
    "content is clear, engaging, and easy to understand for a general audience. "
    "Avoid technical language, present facts objectively, and summarize key "
    "comments from Reddit. Ensure that the overall sentiment expressed in the comments "
    "is accurately reflected. Optimize for highly original content.  Use human-like "
    "natural language, Incorporate emotions, Vary sentence length: Humans don't "
    "always speak in complete sentences, Use light humor to seem more human, however, "
    "be careful not to overdo it. Ensure its written professionally, in a way "
    "that is appropriate for the situation. Format the article using markdown and "
    "include links from the original article/reddit thread."
)

openai.organization = os.environ.get("OPENAI_ORG_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")


def get_metadata_from_reddit_json(data: dict) -> Tuple[str, str]:
    """
    Get the title and selftext from the reddit json data.
    """
    child_data = data[0]["data"]["children"][0]["data"]
    title = child_data.get("title")
    selftext = child_data.get("selftext")
    if title is None:
        raise ValueError("Title not found in child data")
    if selftext is None:
        raise ValueError("Selftext not found in child data")
    return title, selftext


def get_body_contents(
    data: Dict[str, Any],
    path: List[str],
) -> List[Tuple[str, str]]:
    """
    Generator function that yields tuples of the form (path, body_content) for
    all dictionaries in the input data with a key of 'body'.
    NOTE: path is potentially useful here for indenting the output
    """
    # If data is a dictionary, check if it has a 'body' key
    if isinstance(data, dict):
        if "body" in data:
            # If the dictionary has a 'body' key, yield the path and value of the 'body'
            path_str = "/".join([str(x) for x in path])
            return [(path_str, "[" + data["author"] + "] " + data["body"])]
        # Iterate through the dictionary's key-value pairs
        result = []
        for key, value in data.items():
            # Recursively call the function with the value and updated path
            result += get_body_contents(value, path + [key])
        return result
    # If data is a list, iterate through the elements
    elif isinstance(data, list):
        result = []
        for index, item in enumerate(data):
            # Recursively call the function with the element and updated path
            result += get_body_contents(item, path + [str(index)])
        return result
    # If data is neither a dictionary nor a list, return an empty list
    else:
        return []


def summarize_prompt(prompt: str, max_summary_length: int) -> str:
    """
    Use OpenAI's GPT-3 model to complete text based on the given prompt.
    """
    response = openai.Completion.create(
        model=GPT_MODEL,
        prompt=prompt,
        max_tokens=MAX_TOKENS - max_summary_length,
    )

    if isinstance(response, dict) and len(response) > 0:
        return response["choices"][0]["text"]
    else:
        print("response=", response)
        return "Error: unable to generate response."


def summarize_body(body: str, max_length: int = MAX_BODY_TOKEN_SIZE) -> str:
    """
    Summarizes a body of text to be at most max_length tokens long.
    """
    if num_tokens_from_string(body) <= max_length:
        return body
    else:
        summary_string = (
            f"summarize this text to under {max_length} GPT-2 tokens:\n" + body
        )

        return summarize_prompt(
            summary_string,
            num_tokens_from_string(summary_string),
        )


def group_bodies_into_chunks(contents: List[Tuple[str, str]]) -> List[str]:
    """
    Concatenate the bodies into an array of newline delimited strings that are
    <MAX_CHUNK_TOKEN_SIZE tokens long
    """
    results = []
    result = ""
    for body_tuple in contents:
        if body_tuple[1]:
            # replace one or more consecutive newline characters
            body_tuple = (body_tuple[0], re.sub(r"\n+", "\n", body_tuple[1]))

            print("length of body_tuple[1] = ", len(body_tuple[1]))
            # TODO: experiment with recursive summarization functions here.
            # constrain result so that it is less than MAX_CHUNK_TOKEN_SIZE tokens
            # if result is greater than max token length of body, summarize it
            # \n == 1 token.
            # The average number of real words per token for GPT-2 is 0.56,
            # hack for now, use string slicing to constrain body length
            result += body_tuple[1][: estimate_word_count(1000)] + "\n"

            if num_tokens_from_string(result) > MAX_CHUNK_TOKEN_SIZE:
                print("cutnow")
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
    num_tokens = num_tokens_from_string(prompt)

    print("token length: " + str(num_tokens))
    response = openai.Completion.create(
        model=GPT_MODEL,
        prompt=prompt,
        temperature=0.9,
        max_tokens=MAX_TOKENS - num_tokens,
    )
    print("prompt=" + prompt)

    if isinstance(response, dict) and len(response) > 0:
        return response["choices"][0]["text"]
    else:
        print("response=", response)
        return "Error: unable to generate response."


def generate_summary(title: str, selftext: str, groups: List[str]) -> str:
    """
    Generate a summary of the reddit thread using OpenAI's GPT-3 model.
    """

    # initialize the prefix with the title and selftext of the reddit thread JSON
    prefix = f"Title: {title}\n{selftext}"

    output = ""

    # use the first group twice because of top comments
    groups.insert(0, groups[0])

    # Use enumerate to get the index and the group in each iteration
    for i, group in enumerate(groups[:MAX_NUMBER_OF_SUMMARIES]):

        prompt = (
            f"{INSTRUCTION_TEXT}\n\n{prefix}\n\nr/{SUBREDDIT} on REDDIT\n"
            f"COMMENTS BEGIN\n{group}\nCOMMENTS END\n\n"
            "Title: "
        )

        summary = complete_chunk(prompt)
        # insert the summary into the prefix
        prefix = f"Title:{summary}"
        # Use format method to insert values into a string
        output += f"\n\n============\nSUMMARY COUNT: {i}\n============\n"
        output += f"PROMPT: {prompt}\n\n{summary}\n===========================\n\n"

    return output


def main():
    """
    download reddit json, generate summary
    """

    # get the reddit json, will exit if there is an error
    reddit_json = request_json_from_url(REDDIT_URL)

    # write raw json output to file for debugging
    with open("output.json", "w", encoding="utf-8") as raw_json_file:
        raw_json_file.write(str(reddit_json))

    # Get the title and selftext from the reddit thread JSON
    title, selftext = get_metadata_from_reddit_json(reddit_json)

    # get an array of body contents
    contents = get_body_contents(reddit_json, [])

    # concatenate the bodies into an array of newline delimited strings
    groups = group_bodies_into_chunks(contents)

    # print groups along with their lengths
    for i, group in enumerate(groups):
        print(f"Group {i} length: {num_tokens_from_string(group)}")

    print("title + selftext = ", num_tokens_from_string(title + selftext))

    # Generate the summary
    # TODO: experiment with recursive summarization functions here. selftext can be long
    output = generate_summary(title, selftext[: estimate_word_count(500)], groups)

    print(output)

    save_output(title, output)


if __name__ == "__main__":
    main()
