"""Data types for the application."""
from typing import Dict, Optional, TypedDict


class RedditData(TypedDict):
    """Data for a summary."""

    title: str
    selftext: Optional[str]
    subreddit: str
    comments: Optional[str]


class GenerateSettings(TypedDict):
    """Settings for generating a summary."""

    query: str
    chunk_token_length: int
    max_number_of_summaries: int
    max_token_length: int
    selected_model: str
    system_role: str
    selected_model_type: str


class ModelConfig(TypedDict):
    """A model configuration."""

    name: str
    id: str
    default_chunk_token_length: int
    default_number_of_summaries: int
    max_token_length: int


class ConfigVars(TypedDict):
    """Type definition for configuration variables."""

    DEFAULT_GPT_MODEL: str
    ATTACH_DEBUGGER: bool
    WAIT_FOR_CLIENT: bool
    DEFAULT_DEBUG_PORT: int
    DEBUGPY_HOST: str
    DEFAULT_CHUNK_TOKEN_LENGTH: int
    DEFAULT_NUMBER_OF_SUMMARIES: int
    DEFAULT_MAX_TOKEN_LENGTH: int
    LOG_FILE_PATH: str
    LOG_COLORS: Dict[str, str]
    REDDIT_URL: str
    LOG_NAME: str
    APP_TITLE: str
    MAX_BODY_TOKEN_SIZE: int
    DEFAULT_QUERY_TEXT: str
    HELP_TEXT: str
    DEFAULT_SYSTEM_ROLE: str
