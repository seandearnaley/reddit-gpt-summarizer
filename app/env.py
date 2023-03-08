"""
This script will take a reddit URL and use OpenAI's GPT-3 model to generate
a summary of the reddit thread.
"""
# Import necessary modules


import os
from typing import TypedDict

from dotenv import load_dotenv
from log_tools import Logger

app_logger = Logger.get_app_logger()


class EnvVars(TypedDict):
    """Type definition for configuration variables."""

    OPENAI_ORG_ID: str
    OPENAI_API_KEY: str


class EnvVarsLoader:
    """Class for loading environment variables."""

    _env_vars = None

    @classmethod
    @Logger.log
    def load_env(cls) -> EnvVars:
        """
        Load the environment variables from the .env file.

        Returns:
            tuple: A tuple of organization ID and API key
        """
        if cls._env_vars is not None:
            return cls._env_vars

        try:
            load_dotenv()
        except FileNotFoundError as exc:
            err_msg = "Could not find .env file. Please create one."
            app_logger.error(err_msg)
            raise FileNotFoundError(err_msg) from exc

        org_id = os.getenv("OPENAI_ORG_ID")
        api_key = os.getenv("OPENAI_API_KEY")

        if org_id is None or api_key is None:
            err_msg = "Missing OpenAI API key or organization ID."
            app_logger.error(err_msg)
            raise ValueError(err_msg)

        env_vars: EnvVars = {"OPENAI_ORG_ID": org_id, "OPENAI_API_KEY": api_key}

        cls._env_vars = env_vars

        return env_vars
