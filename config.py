"""Configuration file for the Reddit Summarizer."""

from datetime import datetime
from typing import Any, Dict

# Constants
DEFAULT_GPT_MODEL: str = "gpt-3.5-turbo"
ATTACH_DEBUGGER: bool = True
WAIT_FOR_CLIENT: bool = False
DEFAULT_DEBUG_PORT: int = 8765
DEBUGPY_HOST: str = "localhost"
DEFAULT_CHUNK_TOKEN_LENGTH: int = 2000
DEFAULT_NUMBER_OF_SUMMARIES: int = 3  # reduce this to 1 for testing
DEFAULT_MAX_TOKEN_LENGTH: int = 4096  # max number of tokens for GPT-3
LOG_FILE_PATH: str = "./logs/log.log"
LOG_COLORS: Dict[str, str] = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}
THREAD_ID: str = (
    "entertainment/comments/1193p9x/daft_punk_announce_new_random_access_memories"
)
REDDIT_URL: str = f"https://www.reddit.com/r/{THREAD_ID}/"  # URL of reddit thread
SUBREDDIT: str = THREAD_ID.split("/", maxsplit=1)[0]
TODAYS_DATE: str = datetime.now().strftime("%Y-%b-%d")
LOG_NAME: str = "reddit_gpt_summarizer_log"
APP_TITLE: str = "Reddit Thread GPT Summarizer"

MAX_BODY_TOKEN_SIZE: int = 1000
DEFAULT_QUERY_TEXT: str = (
    f"(Todays Date: {TODAYS_DATE}) Revise and improve the "
    "article by incorporating relevant information from the comments. Ensure the "
    "content is clear, engaging, and easy to understand for a general audience. "
    "Avoid technical language, present facts objectively, and summarize key "
    "comments from Reddit. Ensure that the overall sentiment expressed in the comments "
    "is accurately reflected. Optimize for highly original content.  Use human-like "
    "natural language, incorporate emotions, vary sentence length: Humans don't "
    "always speak in complete sentences, use light humor to seem more human, however, "
    "be careful not to overdo it. Ensure its written professionally, in a way "
    "that is appropriate for the situation. Format the document using markdown and "
    "include links from the original article/reddit thread."
)
HELP_TEXT: str = """
    #### Help
    Enter the instructions for the model to follow.
    It will generate a summary of the Reddit thread.
    The trick here is to experiment with token lengths and number
    of summaries. The more summaries you generate, the more likely
    you are to get a good summary.
    The more tokens you use, the more likely you are to get a good summary.
    The more tokens you use, the longer it will take to generate
    the summary. The more summaries you generate, the more it will cost you.
    """


def get_config() -> Dict[str, Any]:
    """Returns a dictionary with configuration parameters."""

    config: Dict[str, Any] = {
        "DEFAULT_GPT_MODEL": DEFAULT_GPT_MODEL,
        "DEFAULT_NUMBER_OF_SUMMARIES": DEFAULT_NUMBER_OF_SUMMARIES,
        "DEFAULT_MAX_TOKEN_LENGTH": DEFAULT_MAX_TOKEN_LENGTH,
        "LOG_FILE_PATH": LOG_FILE_PATH,
        "LOG_COLORS": LOG_COLORS,
        "REDDIT_URL": REDDIT_URL,
        "TODAYS_DATE": TODAYS_DATE,
        "ATTACH_DEBUGGER": ATTACH_DEBUGGER,
        "WAIT_FOR_CLIENT": WAIT_FOR_CLIENT,
        "DEFAULT_DEBUG_PORT": DEFAULT_DEBUG_PORT,
        "DEBUGPY_HOST": DEBUGPY_HOST,
        "DEFAULT_CHUNK_TOKEN_LENGTH": DEFAULT_CHUNK_TOKEN_LENGTH,
        "LOG_NAME": LOG_NAME,
        "APP_TITLE": APP_TITLE,
        "MAX_BODY_TOKEN_SIZE": MAX_BODY_TOKEN_SIZE,
        "DEFAULT_QUERY_TEXT": DEFAULT_QUERY_TEXT,
        "HELP_TEXT": HELP_TEXT,
        "SUBREDDIT": SUBREDDIT,
    }

    # def getitem(key: str) -> Any:
    #     if key in config:
    #         return config[key]

    #     raise KeyError(f"{key} is not a valid configuration parameter")

    # config.__getitem__ = getitem

    return config


class Config:
    """Configuration class for the Reddit Summarizer."""

    def __init__(self) -> None:
        self.config: Dict[str, Any] = {
            "DEFAULT_GPT_MODEL": DEFAULT_GPT_MODEL,
            "DEFAULT_NUMBER_OF_SUMMARIES": DEFAULT_NUMBER_OF_SUMMARIES,
            "DEFAULT_MAX_TOKEN_LENGTH": DEFAULT_MAX_TOKEN_LENGTH,
            "LOG_FILE_PATH": LOG_FILE_PATH,
            "LOG_COLORS": LOG_COLORS,
            "REDDIT_URL": REDDIT_URL,
            "ATTACH_DEBUGGER": ATTACH_DEBUGGER,
            "WAIT_FOR_CLIENT": WAIT_FOR_CLIENT,
            "DEFAULT_DEBUG_PORT": DEFAULT_DEBUG_PORT,
            "DEBUGPY_HOST": DEBUGPY_HOST,
            "DEFAULT_CHUNK_TOKEN_LENGTH": DEFAULT_CHUNK_TOKEN_LENGTH,
            "SUBREDDIT": SUBREDDIT,
        }

    def __getitem__(self, key: str) -> Any:
        if key in self.config:
            return self.config[key]

        raise KeyError(f"{key} is not a valid configuration parameter")
