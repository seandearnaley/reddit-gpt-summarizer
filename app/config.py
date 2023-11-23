"""Configuration file for the Reddit Summarizer."""

import json
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, TypeVar

from data_types.summary import ConfigVars, ModelConfig

ModelList = List[ModelConfig]

OPEN_AI_CHAT_TYPE = "OpenAI Chat"
OPEN_AI_INSTRUCT_TYPE = "OpenAI Instruct"
ANTHROPIC_AI_TYPE = "Anthropic Chat"


def load_models_from_json(file_path: str) -> ModelList:
    """Load models from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as json_file:
        models = json.load(json_file)
    return models


# Load models from JSON files
OPEN_AI_CHAT_MODELS = load_models_from_json(
    "app/model_configs/open_ai_chat_models.json"
)
OPEN_AI_INSTRUCT_MODELS = load_models_from_json(
    "app/model_configs/open_ai_instruct_models.json"
)
ANTHROPIC_AI_MODELS = load_models_from_json(
    "app/model_configs/anthropic_ai_models.json"
)


class ConfigLoader:
    """Class for loading configuration variables."""

    CONFIG_VARS: ConfigVars = ConfigVars(
        ATTACH_DEBUGGER=False,
        WAIT_FOR_CLIENT=False,
        DEFAULT_DEBUG_PORT=8765,
        DEBUGPY_HOST="localhost",
        DEFAULT_CHUNK_TOKEN_LENGTH=2000,
        DEFAULT_NUMBER_OF_SUMMARIES=3,  # reduce this to 1 for testing
        DEFAULT_MAX_TOKEN_LENGTH=4096,  # max number of tokens for GPT-3
        LOG_FILE_PATH="./logs/log.log",
        LOG_COLORS={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        REDDIT_URL="https://www.reddit.com/r/OutOfTheLoop/comments/147fcdf/whats_going_on_with_subreddits_going_private_on/",  # noqa: E501 pylint: disable=line-too-long
        LOG_NAME="reddit_gpt_summarizer_log",
        APP_TITLE="Reddit Thread GPT Summarizer",
        MAX_BODY_TOKEN_SIZE=500,
        DEFAULT_QUERY_TEXT=(
            f"(Todays Date: {datetime.now().strftime('%Y-%b-%d')}) Revise and improve"
            " the article by incorporating relevant information from the comments."
            " Ensure the content is clear, engaging, and easy to understand for a"
            " general audience. Avoid technical language, present facts objectively,"
            " and summarize key comments from Reddit. Ensure that the overall"
            " sentiment expressed in the comments is accurately reflected. Optimize"
            " for highly original content. Don't be trolled by joke comments. Ensure"
            " its written professionally, in a way that is appropriate for the"
            " situation. Format the document using markdown and include links from the"
            " original article/reddit thread."
        ),
        DEFAULT_SYSTEM_ROLE="You are a helpful assistant.",
        HELP_TEXT=(
            "#### Help\nEnter the instructions for the model to follow.\nIt will"
            " generate a summary of the Reddit thread.\nThe trick here is to experiment"
            " with token lengths and number\nof summaries. The more summaries you"
            " generate, the more likely\nyou are to get a good summary.\nThe more"
            " tokens you use, the more likely you are to get a good summary.\nThe more"
            " tokens you use, the longer it will take to generate\nthe summary. The"
            " more summaries you generate, the more it will cost you."
        ),
    )

    @classmethod
    def get_config(cls) -> ConfigVars:
        """Returns a dictionary with configuration parameters."""
        return cls.CONFIG_VARS


R = TypeVar("R")


def with_config(func: Callable[..., R]) -> Callable[..., R]:
    """
    A decorator to inject environment variables into a function.

    Args:
        func (Callable[..., ReturnType]): The function to be decorated.

    Returns:
        Callable[..., ReturnType]: The decorated function with injected environment
        variables.
    """

    @wraps(func)
    def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> R:
        config: ConfigVars = ConfigLoader.get_config()
        return func(*args, config=config, **kwargs)

    return wrapper
