"""Configuration file for the Reddit Summarizer."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any, TypeVar

from pydantic import BaseModel, Field

R = TypeVar("R")


class ModelConfig(BaseModel):
    name: str
    id: str
    default_chunk_token_length: int
    default_number_of_summaries: int
    max_token_length: int
    max_context_length: int


class LogColors(BaseModel):
    DEBUG: str = Field(default="cyan")
    INFO: str = Field(default="green")
    WARNING: str = Field(default="yellow")
    ERROR: str = Field(default="red")
    CRITICAL: str = Field(default="bold_red")

    def get(self, key: str, default: str = "") -> str:
        return getattr(self, key, default)


class ConfigVars(BaseModel):
    ATTACH_DEBUGGER: bool = False
    WAIT_FOR_CLIENT: bool = False
    DEFAULT_DEBUG_PORT: int = 8765
    DEBUGPY_HOST: str = "localhost"
    DEFAULT_CHUNK_TOKEN_LENGTH: int = 2000
    DEFAULT_NUMBER_OF_SUMMARIES: int = 3  # reduce this to 1 for testing
    DEFAULT_MAX_TOKEN_LENGTH: int = 4096  # max number of tokens for GPT-3
    LOG_FILE_PATH: str = "./logs/log.log"
    LOG_COLORS: LogColors = Field(default_factory=LogColors)
    REDDIT_URL: str = "https://www.reddit.com/r/OutOfTheLoop/comments/147fcdf/whats_going_on_with_subreddits_going_private_on/"
    LOG_NAME: str = "reddit_gpt_summarizer_log"
    APP_TITLE: str = "Reddit Thread GPT Summarizer"
    MAX_BODY_TOKEN_SIZE: int = 500
    DEFAULT_QUERY_TEXT: str = (
        f"(Today's Date: {datetime.now().strftime('%Y-%b-%d')}) Revise and improve"
        " the article by incorporating relevant information from the comments."
        " Ensure the content is clear, engaging, and easy to understand for a"
        " general audience. Avoid technical language, present facts objectively,"
        " and summarize key comments from Reddit. Ensure that the overall"
        " sentiment expressed in the comments is accurately reflected. Optimize"
        " for highly original content. Don't be misled by joke comments. Ensure"
        " it's written professionally, in a way that is appropriate for the"
        " situation. Format the document using markdown and include links from the"
        " original article/Reddit thread."
    )
    DEFAULT_SYSTEM_ROLE: str = "You are a helpful assistant."
    HELP_TEXT: str = (
        "#### Help\nEnter the instructions for the model to follow.\nIt will"
        " generate a summary of the Reddit thread.\nThe trick here is to experiment"
        " with token lengths and number\nof summaries. The more summaries you"
        " generate, the more likely\nyou are to get a good summary.\nThe more"
        " tokens you use, the more likely you are to get a good summary.\nThe more"
        " tokens you use, the longer it will take to generate\nthe summary. The"
        " more summaries you generate, the more it will cost you."
    )


def load_models_from_json(file_path: str) -> list[ModelConfig]:
    """Load models from a JSON file."""
    with open(file_path, encoding="utf-8") as json_file:
        models_data = json.load(json_file)
    return [ModelConfig(**model_data) for model_data in models_data]


# Load models from JSON files
MODELS = load_models_from_json(
    "app/model_configs/models.json",
)


def with_config(func: Callable[..., R]) -> Callable[..., R]:
    """
    A decorator to inject configuration variables into a function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function with injected configuration variables.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        config = ConfigVars()
        return func(*args, config=config, **kwargs)

    return wrapper
