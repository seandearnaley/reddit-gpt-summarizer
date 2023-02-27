"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


import logging
import os
from typing import Tuple

from dotenv import load_dotenv

from config import ATTACH_DEBUGGER, DEBUGPY_HOST, DEFAULT_DEBUG_PORT, WAIT_FOR_CLIENT
from debug_tools import setup_debugpy
from log_tools import app_logger, log
from services.ui import render_layout
from streamlit_setup import st


def load_env() -> Tuple[str, str, logging.Logger]:
    """
    Load the environment variables from the .env file.

    Returns:
        tuple: A tuple of organization ID and API key + logging instance.
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

    return org_id, api_key, app_logger


@log
def main() -> None:
    """Main entry point for the app."""
    app_logger.info("Loading layout")
    setup_debugpy(
        st,
        app_logger,
        flag=ATTACH_DEBUGGER,
        wait_for_client=WAIT_FOR_CLIENT,
        host=DEBUGPY_HOST,
        port=DEFAULT_DEBUG_PORT,
    )
    render_layout(*load_env())


if __name__ == "__main__":
    main()
