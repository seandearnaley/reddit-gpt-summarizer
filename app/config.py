"""Configuration file for the Reddit Summarizer."""

from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, TypeVar

from data_types.summary import ConfigVars, ModelConfig

ModelList = List[ModelConfig]

OPEN_AI_CHAT_TYPE = "OpenAI Chat"
OPEN_AI_INSTRUCT_TYPE = "OpenAI Instruct"
ANTHROPIC_AI_TYPE = "Anthropic Chat"

OPEN_AI_CHAT_MODELS: ModelList = [
    {
        "name": "GPT 3.5 Turbo",
        "id": "gpt-3.5-turbo",
        "default_chunk_token_length": 2000,
        "default_number_of_summaries": 3,
        "max_token_length": 4096,
    },
    {
        "name": "GPT 4 8k",
        "id": "gpt-4",
        "default_chunk_token_length": 4096,
        "default_number_of_summaries": 3,
        "max_token_length": 8192,
    },
    {
        "name": "GPT 4 32k",
        "id": "gpt-4-32k",
        "default_chunk_token_length": 8192,
        "default_number_of_summaries": 3,
        "max_token_length": 32768,
    },
]

OPEN_AI_INSTRUCT_MODELS: ModelList = [
    {
        "name": "Text Davinci 003",
        "id": "text-davinci-003",
        "default_chunk_token_length": 2000,
        "default_number_of_summaries": 3,
        "max_token_length": 4097,
    },
    {
        "name": "Text Davinci 002",
        "id": "text-davinci-002",
        "default_chunk_token_length": 2000,
        "default_number_of_summaries": 3,
        "max_token_length": 4097,
    },
    {
        "name": "Text Curie 001",
        "id": "text-curie-001",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
    {
        "name": "Text Babbage 001",
        "id": "text-babbage-001",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
    {
        "name": "Text Ada 001",
        "id": "text-ada-001",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
    {
        "name": "Text Davinci",
        "id": "davinci",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
    {
        "name": "Text Curie",
        "id": "curie",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
    {
        "name": "Text Babbage",
        "id": "babbage",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
    {
        "name": "Text Ada",
        "id": "ada",
        "default_chunk_token_length": 1000,
        "default_number_of_summaries": 3,
        "max_token_length": 2049,
    },
]

ANTHROPIC_AI_MODELS: ModelList = [
    {
        "name": "Claude v1",
        "id": "claude-v1",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
    {
        "name": "Claude v1 100k",
        "id": "claude-v1-100k",
        "default_chunk_token_length": 50000,
        "default_number_of_summaries": 2,
        "max_token_length": 100000,
    },
    {
        "name": "Claude Instant v1",
        "id": "claude-instant-v1",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
    {
        "name": "Claude Instant v1 100k",
        "id": "claude-instant-v1-100k",
        "default_chunk_token_length": 10000,
        "default_number_of_summaries": 1,
        "max_token_length": 100000,
    },
    {
        "name": "Claude v1.3",
        "id": "claude-v1.3",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
    {
        "name": "Claude v1.3 100k",
        "id": "claude-v1.3-100k",
        "default_chunk_token_length": 50000,
        "default_number_of_summaries": 2,
        "max_token_length": 100000,
    },
    {
        "name": "Claude v1.2",
        "id": "claude-v1.2",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
    {
        "name": "Claude v1.0",
        "id": "claude-v1.0",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
    {
        "name": "Claude Instant v1.1",
        "id": "claude-instant-v1.1",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
    {
        "name": "Claude Instant v1.1 100k",
        "id": "claude-instant-v1.1-100k",
        "default_chunk_token_length": 50000,
        "default_number_of_summaries": 2,
        "max_token_length": 100000,
    },
    {
        "name": "Claude Instant v1.0",
        "id": "claude-instant-v1.0",
        "default_chunk_token_length": 4500,
        "default_number_of_summaries": 3,
        "max_token_length": 9000,
    },
]


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
        REDDIT_URL="https://www.reddit.com/r/entertainment/comments/1193p9x/daft_punk_announce_new_random_access_memories/",  # noqa: E501 pylint: disable=line-too-long
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
            " more summaries you generate, the more it will cost you.\n\nNOTE: as of"
            " 5/22/23 GPT-4 32k is not commonly available.\nAlso note: older OpenAI"
            " Instruct models mostly produce garbage but try out Text Davinci 003, it's"
            " not bad.\nAnthropic's 100k models can usually handle entire Reddit"
            " threads without recursion"
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
