"""
UI functions
"""
# Import necessary modules

import logging

import streamlit as st
from config import ConfigVars
from data_types.summary import GenerateSettings
from generate_data import generate_summary_data, get_reddit_praw
from ui.settings import render_settings
from utils.common import is_valid_reddit_url, replace_last_token_with_json, save_output

config = ConfigVars()


def render_input_box() -> str | None:
    """
    Render the input box for the reddit URL and return its value.
    """
    reddit_url: str | None = st.text_area("Enter REDDIT URL:", config.REDDIT_URL)
    if not reddit_url:
        return None

    if not is_valid_reddit_url(reddit_url):
        st.error("Please enter a valid Reddit URL")
        return None
    return reddit_url


def render_output(
    reddit_url: str,
    app_logger: logging.Logger | None = None,
    settings: GenerateSettings | None = None,
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
            progress: int,
            idx: int,
            prompt: str,
            summary: str,
        ) -> None:
            my_bar.progress(progress, text=progress_text)
            with st.expander(f"Prompt {idx}"):
                st.text(prompt)
            st.subheader(f"Response: {idx}")
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
    app_logger: logging.Logger | None = None,
    reddit_url: str | None = None,
    settings: GenerateSettings | None = None,
) -> None:
    """
    Render the layout of the app.
    """

    st.header(config.APP_TITLE)

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
