"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


import streamlit as st
from config import ConfigLoader, ConfigVars
from debug_tools import Debugger
from log_tools import Logger
from ui.render import render_layout

app_logger = Logger.get_app_logger()


def main(config: ConfigVars) -> None:
    """Main entry point for the app."""
    app_logger.info("Loading layout")

    # Set page configuration, must be done before rendering layout
    st.set_page_config(page_title=config["APP_TITLE"], page_icon="🤖", layout="wide")

    Debugger.setup_debugpy(
        st,
        app_logger,
        flag=config["ATTACH_DEBUGGER"],
        wait_for_client=config["WAIT_FOR_CLIENT"],
        host=config["DEBUGPY_HOST"],
        port=config["DEFAULT_DEBUG_PORT"],
    )

    render_layout(app_logger=app_logger)


if __name__ == "__main__":
    _config = ConfigLoader.get_config()
    main(_config)
