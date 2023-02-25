"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


from typing import Dict, List, Optional

import streamlit as st

import config
from presets import presets
from utils.common import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
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


def generate_data(
    instruction: str,
    chunk_token_length: int,
    number_of_summaries: int,
    max_token_length: int,
    json_url: str,
    subreddit: str,
) -> Optional[Dict[str, str | List[str]]]:
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

    # concatenate the bodies into an array of newline delimited strings
    groups = group_bodies_into_chunks(contents, chunk_token_length)

    logger.debug(
        "title + selftext string length as tokens =%s",
        num_tokens_from_string(title + selftext),
    )

    # Generate the summary, really should do recursive summary on selftext here
    output = ""

    # use the first group twice because of top comments
    groups.insert(0, groups[0])

    prompts: List[str] = []
    summaries: List[str] = []

    # Use enumerate to get the index and the group in each iteration
    for summary_num, comment_group in enumerate(groups[:number_of_summaries]):
        prompt = (
            f"{instruction}\n\nTitle:"
            f" {title}\n{selftext[: estimate_word_count(500)]}\n\nr/{subreddit} on"
            f" REDDIT\nCOMMENTS BEGIN\n{comment_group}\nCOMMENTS END\n\nTitle: "
        )
        summary = complete_text(
            prompt, max_token_length - num_tokens_from_string(prompt)
        )
        prompts.append(prompt)
        summaries.append(summary)

        # Use format method to insert values into a string
        output += f"============\nSUMMARY COUNT: {summary_num}\n============\n"
        output += f"PROMPT: {prompt}\n\n{summary}\n===========================\n\n"

    return {
        "title": title,
        "selftext": selftext,
        "output": output,
        "prompts": prompts,
        "summaries": summaries,
        "groups": groups,
    }


def render_layout() -> None:
    """
    Render the layout of the app.
    """

    st.header("Reddit Thread GPT Summarizer")
    # Create an input box for url

    reddit_url = st.text_area("Enter REDDIT URL:", config.REDDIT_URL)
    if not is_valid_reddit_url(reddit_url):
        st.error("Please enter a valid Reddit URL ending in '.json'.")
        return

    with st.expander("Edit Settings"):
        instruction_text: str = st.text_area(
            "Instructions", config.DEFAULT_INSTRUCTION_TEXT, height=250
        )
        model = st.radio("Select Model", list(presets.keys()))

        if model:
            st.text(f"You selected model {model}. Here are the parameters:")
            st.text(presets[model])

        chunk_token_length = int(
            st.number_input(
                "Chunk Token Length", value=config.DEFAULT_CHUNK_TOKEN_LENGTH, step=1
            )
        )

        number_of_summaries = int(
            st.number_input(
                "Number of Summaries",
                value=config.DEFAULT_NUMBER_OF_SUMMARIES,
                min_value=1,
                max_value=10,
                step=1,
            )
        )
        max_token_length = int(
            st.number_input(
                "Max Token Length", value=config.DEFAULT_MAX_TOKEN_LENGTH, step=1
            )
        )

    btn = st.button("Generate it!")

    # Create a button to submit the url
    if btn:
        summary_placeholder = st.empty()

        with summary_placeholder.container():
            with st.spinner("Wait for it..."):
                result = generate_data(
                    instruction_text,
                    chunk_token_length,
                    number_of_summaries,
                    max_token_length,
                    reddit_url,
                    config.SUBREDDIT,
                )

                if result is None:
                    st.error("No Summary Data")
                    st.stop()

                title, selftext, output, prompts, summaries, groups = (
                    result["title"],
                    result["selftext"],
                    result["output"],
                    result["prompts"],
                    result["summaries"],
                    result["groups"],
                )

                save_output(str(title), str(output))

                st.subheader("Original")
                st.subheader(title)
                st.text(selftext)

                # print groups along with their lengths

                for i, group in enumerate(groups):
                    with st.expander(
                        f"Group {i} length {num_tokens_from_string(group)} tokens"
                    ):
                        st.code(group)

                st.subheader("Generated")
            for i, summary in enumerate(summaries):
                with st.expander(f"Prompt {i}"):
                    st.code(prompts[i])
                st.subheader(f"OpenAI Completion Reponse: {i}")
                st.markdown(summary)

            st.success("Done!")
            clear_btn = st.button("Clear")

            if clear_btn:
                summary_placeholder.empty()


if __name__ == "__main__":
    render_layout()
