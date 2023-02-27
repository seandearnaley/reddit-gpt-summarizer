"""Configuration file for the Reddit Summarizer."""

from datetime import datetime

# Constants
DEFAULT_GPT_MODEL = "text-davinci-003"
ATTACH_DEBUGGER = False
WAIT_FOR_CLIENT = False
DEFAULT_DEBUG_PORT = 8765
DEBUGPY_HOST = "localhost"
DEFAULT_CHUNK_TOKEN_LENGTH = 2000
DEFAULT_NUMBER_OF_SUMMARIES = 3  # reduce this to 1 for testing
DEFAULT_MAX_TOKEN_LENGTH = 3000  # max number of tokens for GPT-3
LOG_FILE_PATH = "./logs/log.log"
LOG_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}
THREAD_ID = (
    "entertainment/comments/1193p9x/daft_punk_announce_new_random_access_memories"
)
REDDIT_URL = f"https://www.reddit.com/r/{THREAD_ID}/"  # URL of reddit thread
SUBREDDIT = THREAD_ID.split("/", maxsplit=1)[0]
TODAYS_DATE: str = datetime.now().strftime("%Y-%b-%d")
LOG_NAME = "reddit_gpt_summarizer_log"
APP_TITLE = "Reddit Thread GPT Summarizer"

MAX_BODY_TOKEN_SIZE = 1000  # not in use yet
DEFAULT_QUERY_TEXT = (
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
HELP_TEXT = """
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
