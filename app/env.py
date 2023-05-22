"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules

import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from log_tools import Logger

app_logger = Logger.get_app_logger()


class EnvVars(TypedDict):
    """Type definition for configuration variables."""

    OPENAI_ORG_ID: str
    OPENAI_API_KEY: str
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USERNAME: Optional[str]
    REDDIT_PASSWORD: Optional[str]
    REDDIT_USER_AGENT: str
    ANTHROPIC_API_KEY: str


class EnvVarsLoader:
    """Class for loading environment variables."""

    _env_vars = None

    @staticmethod
    @Logger.log
    def load_env() -> EnvVars:
        """
        Load the environment variables from the .env file.

        Returns:
            tuple: A tuple of organization ID and API key
        """
        if EnvVarsLoader._env_vars is not None:
            return EnvVarsLoader._env_vars

        try:
            load_dotenv()
        except FileNotFoundError as exc:
            err_msg = "Could not find .env file. Please create one."
            app_logger.error(err_msg)
            raise exc

        org_id = os.getenv("OPENAI_ORG_ID")
        api_key = os.getenv("OPENAI_API_KEY")
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        reddit_username = os.getenv("REDDIT_USERNAME")
        reddit_password = os.getenv("REDDIT_PASSWORD")
        reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
        anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]

        if org_id is None or api_key is None:
            err_msg = "Missing OpenAI API key or organization ID."
            app_logger.error(err_msg)
            raise ValueError(err_msg)

        if (
            reddit_client_id is None
            or reddit_client_secret is None
            or reddit_user_agent is None
        ):
            err_msg = "Missing Reddit client ID or client secret."
            app_logger.error(err_msg)
            raise ValueError(err_msg)

        env_vars: EnvVars = {
            "OPENAI_ORG_ID": org_id,
            "OPENAI_API_KEY": api_key,
            "REDDIT_CLIENT_ID": reddit_client_id,
            "REDDIT_CLIENT_SECRET": reddit_client_secret,
            "REDDIT_USERNAME": reddit_username,
            "REDDIT_PASSWORD": reddit_password,
            "REDDIT_USER_AGENT": reddit_user_agent,
            "ANTHROPIC_API_KEY": anthropic_api_key,
        }

        EnvVarsLoader._env_vars = env_vars

        return env_vars
