"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules

import re
from datetime import datetime
from typing import Any, Dict, Generator, List, Tuple, Union

import streamlit as st

from utils.common import request_json_from_url, save_output
from utils.logger import logger
from utils.openai import complete_text, estimate_word_count, num_tokens_from_string

# Constants
MAX_CHUNK_TOKEN_SIZE = 500
MAX_BODY_TOKEN_SIZE = 1000  # not in use yet
MAX_NUMBER_OF_SUMMARIES = 3  # reduce this to 1 for testing
MAX_TOKENS = 3000  # max number of tokens for GPT-3
THREAD_ID = (
    "entertainment/comments/1193p9x/daft_punk_announce_new_random_access_memories"
)
REDDIT_URL = f"https://www.reddit.com/r/{THREAD_ID}.json"  # URL of reddit thread
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


def get_metadata_from_reddit_json(data: list[dict[str, Any]]) -> Tuple[str, str]:
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
    data: Union[Dict[str, Any], List[Any], str], path: List[str]
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
            yield from get_body_contents(value, path + [key])
    # If data is a list, iterate through the elements
    elif isinstance(data, list):
        for index, item in enumerate(data):
            # Recursively call the function with the element and updated path
            yield from get_body_contents(item, path + [repr(index)])


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

        return complete_text(summary_string, num_tokens_from_string(summary_string))


def group_bodies_into_chunks(contents: List[Tuple[str, str]]) -> List[str]:
    """
    Concatenate the bodies into an array of newline delimited strings that are
    <MAX_CHUNK_TOKEN_SIZE tokens long
    """
    results: List[str] = []
    result = ""
    for body_tuple in contents:
        if body_tuple[1]:
            # replace one or more consecutive newline characters
            body_tuple = (body_tuple[0], re.sub(r"\n+", "\n", body_tuple[1]))

            logger.debug("length of body_tuple[1] = %s", len(body_tuple[1]))
            # constrain result so that it is less than MAX_CHUNK_TOKEN_SIZE tokens
            # if result is greater than max token length of body, summarize it
            # \n == 1 token.
            # The average number of real words per token for GPT-2 is 0.56,
            # hack for now, use string slicing to constrain body length
            result += body_tuple[1][: estimate_word_count(1000)] + "\n"

            if num_tokens_from_string(result) > MAX_CHUNK_TOKEN_SIZE:
                logger.debug("cutnow")
                results.append(result)
                result = ""
    if result:
        results.append(result)
    return results


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

        st.subheader("summary prompt: " + str(i + 1))
        st.code(prompt)

        summary = complete_text(prompt, MAX_TOKENS - num_tokens_from_string(prompt))
        # insert the summary into the prefix

        st.subheader("openai_response: " + str(i + 1))
        st.code(summary)

        prefix = f"Title:{summary}"
        # Use format method to insert values into a string
        output += f"============\nSUMMARY COUNT: {i}\n============\n"
        output += f"PROMPT: {prompt}\n\n{summary}\n===========================\n\n"

    return output


def process(json_url: str = REDDIT_URL):
    """
    Process the reddit thread JSON and generate a summary.
    """
    # get the reddit json, will exit if there is an error
    reddit_json = request_json_from_url(json_url)

    # write raw json output to file for debugging
    with open("output.json", "w", encoding="utf-8") as raw_json_file:
        raw_json_file.write(str(reddit_json))

    # Get the title and selftext from the reddit thread JSON
    title, selftext = get_metadata_from_reddit_json(reddit_json)

    st.header(title)
    st.text(selftext)
    # get an array of body contents
    contents = list(get_body_contents(reddit_json, []))

    if not contents:
        logger.error("No body contents found")
        st.error("No body contents found")
        st.stop()

    # concatenate the bodies into an array of newline delimited strings
    groups = group_bodies_into_chunks(contents)
    length_subheading: str = "title + selftext string length as tokens =" + str(
        num_tokens_from_string(title + selftext)
    )

    logger.debug(length_subheading)
    st.text(length_subheading)
    # print groups along with their lengths
    for i, group in enumerate(groups):
        logger.debug("Group %s length: %s", i, num_tokens_from_string(group))

        st.text(
            f"Group {i} length {num_tokens_from_string(group)}",
        )

        st.code(group)

    # Generate the summary
    output = generate_summary(title, selftext[: estimate_word_count(500)], groups)

    logger.info(output)

    save_output(title, output)
    return output


st.header("Reddit Thread GPT Summarizer")
placeholder = st.empty()

# Create an input box for url
with placeholder.container():
    reddit_url = st.text_area("Enter REDDIT URL:", REDDIT_URL)
    btn = st.button("Get data")

# Create a button to submit the url
if btn:
    if not reddit_url.endswith(".json"):
        st.error("must end with .json")

    placeholder.empty()
    summary_placeholder = st.empty()

    with summary_placeholder.container():
        with st.spinner("Wait for it..."):
            summary_data = process(reddit_url)
            if not summary_data:
                # Display error message if response is invalid
                st.error("No Summary Data")

        st.success("Done!")
        clear_btn = st.button("Clear")

        if clear_btn:
            summary_placeholder = st.empty()
