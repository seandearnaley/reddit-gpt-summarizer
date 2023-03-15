"""Data types for the application."""
from typing import Optional, TypedDict


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
