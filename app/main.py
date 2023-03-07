"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


import os
from typing import Tuple

import streamlit as st
from config import ConfigVars, get_config
from debug_tools import setup_debugpy
from dotenv import load_dotenv
from log_tools import app_logger, log
from ui.render import render_layout


@log
def load_env() -> Tuple[str, str]:
    """
    Load the environment variables from the .env file.

    Returns:
        tuple: A tuple of organization ID and API key
    """
    try:
        load_dotenv()
    except FileNotFoundError:
        err_msg = "Could not find .env file. Please create one."
        app_logger.error(err_msg)
        st.error(err_msg)
        st.stop()

    org_id = os.getenv("OPENAI_ORG_ID")
    api_key = os.getenv("OPENAI_API_KEY")

    if org_id is None or api_key is None:
        err_msg = "Missing OpenAI API key or organization ID."
        app_logger.error(err_msg)
        st.error(err_msg)
        st.stop()

    return org_id, api_key


def main(config: ConfigVars) -> None:
    """Main entry point for the app."""
    app_logger.info("Loading layout")

    # Set page configuration, must be done before rendering layout
    st.set_page_config(page_title=config["APP_TITLE"], page_icon="🤖", layout="wide")

    setup_debugpy(
        st,
        app_logger,
        flag=config["ATTACH_DEBUGGER"],
        wait_for_client=config["WAIT_FOR_CLIENT"],
        host=config["DEBUGPY_HOST"],
        port=config["DEFAULT_DEBUG_PORT"],
    )

    render_layout(*load_env(), app_logger=app_logger)


if __name__ == "__main__":
    _config = get_config()
    main(_config)
