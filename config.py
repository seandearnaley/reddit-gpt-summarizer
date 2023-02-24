"""Configuration file for the Reddit Summarizer."""

from datetime import datetime

# Constants
DEFAULT_CHUNK_TOKEN_LENGTH = 2000
DEFAULT_NUMBER_OF_SUMMARIES = 3  # reduce this to 1 for testing
DEFAULT_MAX_TOKEN_LENGTH = 3000  # max number of tokens for GPT-3
THREAD_ID = (
    "entertainment/comments/1193p9x/daft_punk_announce_new_random_access_memories"
)
REDDIT_URL = f"https://www.reddit.com/r/{THREAD_ID}.json"  # URL of reddit thread
SUBREDDIT = THREAD_ID.split("/", maxsplit=1)[0]
TODAYS_DATE: str = datetime.now().strftime("%Y-%b-%d")


DEFAULT_INSTRUCTION_TEXT = (
    f"(Todays Date: {TODAYS_DATE}) Revise and improve the "
    "article by incorporating relevant information from the comments. Ensure the "
    "content is clear, engaging, and easy to understand for a general audience. "
    "Avoid technical language, present facts objectively, and summarize key "
    "comments from Reddit. Ensure that the overall sentiment expressed in the comments "
    "is accurately reflected. Optimize for highly original content.  Use human-like "
    "natural language, incorporate emotions, vary sentence length: Humans don't "
    "always speak in complete sentences, use light humor to seem more human, however, "
    "be careful not to overdo it. Ensure its written professionally, in a way "
    "that is appropriate for the situation. Format the article using markdown and "
    "include links from the original article/reddit thread."
)
