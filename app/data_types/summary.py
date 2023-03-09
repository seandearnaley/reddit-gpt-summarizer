"""Data types for the application."""
from typing import TypedDict


class RedditData(TypedDict):
    """Data for a summary."""

    title: str | None
    selftext: str | None
    subreddit: str | None
    comments: str | None


class GenerateSettings(TypedDict):
    """Settings for generating a summary."""

    query: str
    chunk_token_length: int
    max_number_of_summaries: int
    max_token_length: int
    selected_model: str
    selected_model: str
    system_role: str
