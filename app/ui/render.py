"""
UI functions
"""
# Import necessary modules

import logging
from typing import Optional

import streamlit as st
from config import ConfigLoader
from data_types.summary import GenerateSettings
from services.generate_data import generate_summary_data, get_reddit_praw
from services.openai_methods import get_models
from utils.common import is_valid_reddit_url, replace_last_token_with_json, save_output
from utils.streamlit_decorators import expander_decorator

config = ConfigLoader.get_config()


def render_input_box() -> Optional[str]:
    """
    Render the input box for the reddit URL and return its value.
    """
    reddit_url: Optional[str] = st.text_area("Enter REDDIT URL:", config["REDDIT_URL"])
    if not reddit_url:
        return None

    if not is_valid_reddit_url(reddit_url):
        st.error("Please enter a valid Reddit URL")
        return None
    return reddit_url


@expander_decorator("Edit Settings")
def render_settings() -> GenerateSettings:
    """
    Render the settings for the app and return the model and settings.
    """
    system_role: str = st.text_input("System Role", config["DEFAULT_SYSTEM_ROLE"])
    query_text: str = st.text_area(
        "Instructions", config["DEFAULT_QUERY_TEXT"], height=250
    )

    col1, col2 = st.columns(2)
    with col1:
        models = get_models()
        model_ids = [model["id"] for model in models]  # type: ignore
        filtered_list = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "get-4"]
        model_ids_sorted = sorted(filtered_list)
        default_model_index = model_ids_sorted.index(config["DEFAULT_GPT_MODEL"])
        selected_model = st.radio(
            label="Select Model",
            options=model_ids_sorted,
            index=default_model_index,
        )

        if selected_model:
            st.text(f"You selected model {selected_model}. Here are the parameters:")
            st.text(models[model_ids.index(selected_model)])  # type: ignore
        else:
            st.text("Select a model")
            st.stop()

        chunk_token_length = st.number_input(
            label="Chunk Token Length",
            value=config["DEFAULT_CHUNK_TOKEN_LENGTH"],
            step=1,
        )

        max_number_of_summaries = st.number_input(
            label="Max Number of Summaries",
            value=config["DEFAULT_NUMBER_OF_SUMMARIES"],
            min_value=1,
            max_value=10,
            step=1,
        )

        max_token_length = st.number_input(
            label="Max Token Length",
            value=config["DEFAULT_MAX_TOKEN_LENGTH"],
            step=1,
        )
    with col2:
        st.markdown(config["HELP_TEXT"])

    return {
        "system_role": system_role,
        "query": query_text,
        "chunk_token_length": int(chunk_token_length),
        "max_number_of_summaries": int(max_number_of_summaries),
        "max_token_length": int(max_token_length),
        "selected_model": selected_model,
    }


def render_output(
    reddit_url: str,
    app_logger: Optional[logging.Logger] = None,
    settings: Optional[GenerateSettings] = None,
) -> None:
    """
    Render the placeholder for the summary.
    """
    output_placeholder = st.empty()

    with output_placeholder.container():
        if app_logger:
            app_logger.info("Generating summary data")

        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        def progress_callback(
            progress: int, idx: int, prompt: str, summary: str
        ) -> None:
            my_bar.progress(progress, text=progress_text)
            with st.expander(f"Prompt {idx}"):
                st.text(prompt)
            st.subheader(f"ChatGPT Response: {idx}")
            st.markdown(summary)

        try:
            reddit_data = get_reddit_praw(
                json_url=replace_last_token_with_json(reddit_url),
                logger=app_logger,
            )

            if not reddit_data:
                st.error("no reddit data")
                st.stop()

            st.text("Original Content:")
            st.subheader(reddit_data["title"])
            st.text(reddit_data["selftext"])

            str_output = generate_summary_data(
                settings=settings,
                reddit_data=reddit_data,
                logger=app_logger,
                progress_callback=progress_callback,
            )

            save_output(str(reddit_data["title"]), str(str_output))

            if app_logger:
                app_logger.info("Summary data generated")

        except Exception as ex:  # pylint: disable=broad-except
            st.error(f"Unexpected error trying to generate_summary_data: {ex}")

        st.success("Done!")

    if st.button("Clear"):
        output_placeholder.empty()


def render_layout(
    app_logger: Optional[logging.Logger] = None,
    reddit_url: Optional[str] = None,
    settings: Optional[GenerateSettings] = None,
) -> None:
    """
    Render the layout of the app.
    """

    st.header(config["APP_TITLE"])

    # Create an input box for url
    if not reddit_url:
        reddit_url = render_input_box()
        if not reddit_url:
            return

    settings = settings or render_settings()

    if not settings:
        st.error("No settings (not sure how this happened)")
        return

    # Create a button to submit the url
    if st.button("Generate it!"):
        render_output(
            app_logger=app_logger,
            settings=settings,
            reddit_url=reddit_url,
        )
