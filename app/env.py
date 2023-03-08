"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


import os
from typing import TypedDict

import streamlit as st
from dotenv import load_dotenv
from log_tools import app_logger, log


class EnvVars(TypedDict):
    """Type definition for configuration variables."""

    OPENAI_ORG_ID: str
    OPENAI_API_KEY: str


@log
def load_env() -> EnvVars:
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

    env_vars: EnvVars = {"OPENAI_ORG_ID": org_id, "OPENAI_API_KEY": api_key}

    return env_vars
