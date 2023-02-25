"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules

import re
from typing import Any, Dict, Generator, List, Tuple, Union

import streamlit as st

import config
from presets import presets
from utils.common import (
    get_metadata_from_reddit_json,
    is_valid_reddit_url,
    request_json_from_url,
    save_output,
)
from utils.logger import logger
from utils.openai import complete_text, estimate_word_count, num_tokens_from_string
from utils.streamlit_debug import StreamlitDebug

debugger = StreamlitDebug()
debugger.set_debugpy(flag=True, wait_for_client=True, host="localhost", port=8765)

# Set page configuration
st.set_page_config(
    page_title="Reddit Thread GPT Summarizer", page_icon="🤖", layout="wide"
)


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

            logger.debug("length of body_tuple[1] = %s", len(body_tuple[1]))
            # constrain result so that it is less than chunk token_length tokens
            # if result is greater than max token length of body, summarize it
            # \n == 1 token.
            # The average number of real words per token for GPT-2 is 0.56,
            # hack for now, use string slicing to constrain body length
            result += body_tuple[1][: estimate_word_count(1000)] + "\n"

            if num_tokens_from_string(result) > token_length:
                logger.debug("cutnow")
                results.append(result)
                result = ""
    if result:
        results.append(result)
    return results


def generate_summary(
    instruction: str,
    title: str,
    selftext: str,
    groups: List[str],
    number_of_summaries: int,
    max_token_length: int,
    subreddit: str,
) -> str:
    """
    Generate a summary of the reddit thread using OpenAI's GPT-3 model.
    """
    output = ""

    # use the first group twice because of top comments
    groups.insert(0, groups[0])

    # Use enumerate to get the index and the group in each iteration
    for summary_num, comment_group in enumerate(groups[:number_of_summaries]):
        prompt = (
            f"{instruction}\n\nTitle: {title}\n{selftext}\n\nr/{subreddit} on"
            f" REDDIT\nCOMMENTS BEGIN\n{comment_group}\nCOMMENTS END\n\nTitle: "
        )

        with st.expander(f"Prompt: {summary_num + 1}"):
            st.code(prompt)

            with st.spinner("Generating summary..."):
                summary = complete_text(
                    prompt, max_token_length - num_tokens_from_string(prompt)
                )
                # insert the summary into the prefix

                st.subheader(f"OpenAI Completion Reponse: {summary_num + 1}")
                st.code(summary)

                # Use format method to insert values into a string
                output += f"============\nSUMMARY COUNT: {summary_num}\n============\n"
                output += (
                    f"PROMPT: {prompt}\n\n{summary}\n===========================\n\n"
                )

    return output


def process(
    instruction: str,
    chunk_token_length: int,
    number_of_summaries: int,
    max_token_length: int,
    json_url: str,
    subreddit: str,
) -> str | None:
    """
    Process the reddit thread JSON and generate a summary.
    """
    try:
        # get the reddit json, will exit if there is an error
        reddit_json = request_json_from_url(json_url)
    except ValueError as exc:
        st.error("Invalid URL. Please enter a valid Reddit URL and try again.")
        logger.exception(exc)
        return None

    # write raw json output to file for debugging
    with open("output.json", "w", encoding="utf-8") as raw_json_file:
        raw_json_file.write(str(reddit_json))

    # Get the title and selftext from the reddit thread JSON
    title, selftext = get_metadata_from_reddit_json(reddit_json)
    # get an array of body contents
    contents = list(get_comment_bodies(reddit_json, []))

    if not contents:
        st.error("No body contents found")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")

        st.subheader(title)
        st.text(selftext)

        # concatenate the bodies into an array of newline delimited strings
        groups = group_bodies_into_chunks(contents, chunk_token_length)

        logger.debug(
            "title + selftext string length as tokens =%s",
            num_tokens_from_string(title + selftext),
        )
        # print groups along with their lengths

        for i, group in enumerate(groups):
            with st.expander(
                f"Group {i} length {num_tokens_from_string(group)} tokens"
            ):
                st.code(group)

    with col2:
        st.subheader("Generated")

        # Generate the summary, really should do recursive summary on selftext here
        output = generate_summary(
            instruction,
            title,
            selftext[: estimate_word_count(500)],
            groups,
            number_of_summaries,
            max_token_length,
            subreddit,
        )

    save_output(title, output)
    return output


def generate_summary_data(
    text: str,
    chunk_token_length: int,
    number_of_summaries: int,
    max_token_length: int,
    url: str,
    subreddit: str,
) -> None:
    """
    Generate a summary of the reddit thread using OpenAI's GPT-3 model.
    """
    if not is_valid_reddit_url(url):
        st.error("Please enter a valid Reddit URL ending in '.json'.")
        return

    summary_placeholder = st.empty()

    with summary_placeholder.container():
        with st.spinner("Wait for it..."):
            summary_data = process(
                text,
                chunk_token_length,
                number_of_summaries,
                max_token_length,
                url,
                subreddit,
            )
            if not summary_data:
                # Display error message if response is invalid
                st.error("No Summary Data")
                return

        st.success("Done!")
        clear_btn = st.button("Clear")

        if clear_btn:
            summary_placeholder.empty()


st.header("Reddit Thread GPT Summarizer")

# Create an input box for url
with st.container():
    reddit_url = st.text_area("Enter REDDIT URL:", config.REDDIT_URL)

    with st.expander("Edit Settings"):
        instruction_text: str = st.text_area(
            "Instructions", config.DEFAULT_INSTRUCTION_TEXT, height=250
        )
        model = st.radio("Select Model", list(presets.keys()))

        if model:
            st.text(f"You selected model {model}. Here are the parameters:")
            st.text(presets[model])
        else:
            st.text("Please select a model.")

        chunk_token_length_input = int(
            st.number_input("Chunk Token Length", config.DEFAULT_CHUNK_TOKEN_LENGTH)
        )

        number_of_summaries_input = int(st.number_input("Number of Summaries", 1, 10))
        max_token_length_input = int(
            st.number_input("Max Token Length", config.DEFAULT_MAX_TOKEN_LENGTH)
        )

    btn = st.button("Generate it!")

# Create a button to submit the url
if btn:
    generate_summary_data(
        instruction_text,
        chunk_token_length_input,
        number_of_summaries_input,
        max_token_length_input,
        reddit_url,
        config.SUBREDDIT,
    )
