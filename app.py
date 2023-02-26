"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


from typing import Dict, List, Optional

from config import (
    ATTACH_DEBUGGER,
    DEFAULT_CHUNK_TOKEN_LENGTH,
    DEFAULT_GPT_MODEL,
    DEFAULT_MAX_TOKEN_LENGTH,
    DEFAULT_NUMBER_OF_SUMMARIES,
    DEFAULT_QUERY_TEXT,
    REDDIT_URL,
    SUBREDDIT,
    WAIT_FOR_CLIENT,
)
from debug_tools import setup_debugpy
from logger import app_logger
from streamlit_setup import st
from utils.common import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
    is_valid_reddit_url,
    replace_last_token_with_json,
    request_json_from_url,
    save_output,
)
from utils.openai import (
    complete_text,
    estimate_word_count,
    get_models,
    num_tokens_from_string,
)

setup_debugpy(
    st,
    app_logger,
    flag=ATTACH_DEBUGGER,
    wait_for_client=WAIT_FOR_CLIENT,
    host="localhost",
    port=8765,
)


def generate_prompts(
    title: str, selftext: str, groups: List[str], query: str, subreddit: str
) -> List[str]:
    """Generate the prompts for the OpenAI API."""
    prompts: List[str] = []
    for comment_group in groups:
        prompt = (
            f"{query}\n\nTitle: "
            f"{title}\n{selftext[: estimate_word_count(500)]}\n\nr/{subreddit} on "
            f"REDDIT\nCOMMENTS BEGIN\n{comment_group}\nCOMMENTS END\n\nTitle: "
        )
        prompts.append(prompt)
    return prompts


def generate_summaries(
    prompts: List[str], max_token_length: int, model: str
) -> List[str]:
    """Generate the summaries from the prompts."""
    summaries: List[str] = []
    for prompt in prompts:
        summary = complete_text(
            prompt, max_token_length - num_tokens_from_string(prompt), model
        )
        summaries.append(summary)
    return summaries


def generate_data(
    query: str,
    chunk_token_length: int,
    number_of_summaries: int,
    max_token_length: int,
    json_url: str,
    model: str,
) -> Optional[Dict[str, str | List[str]]]:
    """
    Process the reddit thread JSON and generate a summary.
    """
    reddit_json = request_json_from_url(json_url)
    if not reddit_json:
        st.error("Invalid URL. Please enter a valid Reddit URL and try again.")
        return None

    title, selftext = get_metadata_from_reddit_json(reddit_json)
    contents = list(get_comment_bodies(reddit_json, []))
    groups = group_bodies_into_chunks(contents, chunk_token_length)
    groups.insert(0, groups[0])

    prompts = generate_prompts(
        title, selftext, groups[:number_of_summaries], query, SUBREDDIT
    )
    summaries = generate_summaries(prompts, max_token_length, model)

    output = ""
    for i, summary in enumerate(summaries):
        prompt = prompts[i]
        output += f"============\nSUMMARY COUNT: {i}\n============\n"
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

    reddit_url = st.text_area("Enter REDDIT URL:", REDDIT_URL)
    if not is_valid_reddit_url(reddit_url):
        st.error("Please enter a valid Reddit URL")
        return

    with st.expander("Edit Settings"):
        query_text: str = st.text_area("Instructions", DEFAULT_QUERY_TEXT, height=250)

        models = get_models()
        model_ids = [model["id"] for model in models]  # type: ignore
        model_ids_sorted = sorted(model_ids)
        default_model_index = model_ids_sorted.index(DEFAULT_GPT_MODEL)
        model = st.radio("Select Model", model_ids_sorted, default_model_index)

        if model:
            st.text(f"You selected model {model}. Here are the parameters:")
            st.text(models[model_ids.index(model)])  # type: ignore
        else:
            st.text("Select a model")
            st.stop()

        chunk_token_length = st.number_input(
            "Chunk Token Length", value=DEFAULT_CHUNK_TOKEN_LENGTH, step=1
        )

        number_of_summaries = st.number_input(
            "Number of Summaries",
            value=DEFAULT_NUMBER_OF_SUMMARIES,
            min_value=1,
            max_value=10,
            step=1,
        )

        max_token_length = st.number_input(
            "Max Token Length", value=DEFAULT_MAX_TOKEN_LENGTH, step=1
        )

    btn = st.button("Generate it!")

    # Create a button to submit the url
    if btn:
        summary_placeholder = st.empty()

        with summary_placeholder.container():
            with st.spinner("Wait for it..."):
                result = generate_data(
                    query_text,
                    int(chunk_token_length),
                    int(number_of_summaries),
                    int(max_token_length),
                    replace_last_token_with_json(reddit_url),
                    model,
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
