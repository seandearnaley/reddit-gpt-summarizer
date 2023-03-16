"""
Reddit Summarizer with ChatGPT

This script will take a Reddit URL and use OpenAI's GPT models to generate
a summary of the Reddit thread. It uses Streamlit for the UI and provides
debugging tools and a logger.
"""

# External libraries
import streamlit as st

# Configuration and utilities
from config import ConfigLoader, ConfigVars
from debug_tools import Debugger
from log_tools import Logger

# UI components
from ui.render import render_layout

# Set up the application logger
app_logger = Logger.get_app_logger()


def main(config: ConfigVars) -> None:
    """
    Main entry point for the app.

    Args:
        config (ConfigVars): A dictionary containing the
        application's configuration variables.
    """
    app_logger.info("Loading layout")

    # Set up the page configuration before rendering the layout
    st.set_page_config(page_title=config["APP_TITLE"], page_icon="🤖", layout="wide")

    # Set up the debugger if enabled in the configuration
    Debugger.setup_debugpy(
        st,
        app_logger,
        flag=config["ATTACH_DEBUGGER"],
        wait_for_client=config["WAIT_FOR_CLIENT"],
        host=config["DEBUGPY_HOST"],
        port=config["DEFAULT_DEBUG_PORT"],
    )

    # Render the main layout of the application
    render_layout(app_logger=app_logger)


if __name__ == "__main__":
    # Load the configuration and start the application
    _config = ConfigLoader.get_config()
    main(_config)
