"""Data types for the application."""
from typing import Any, Dict, List, TypedDict


class RedditMeta(TypedDict):
    """Data for a summary."""

    title: str
    selftext: str
    subreddit: str
    reddit_json: List[Dict[str, Any]]


class GenerateSettings(TypedDict):
    """Settings for generating a summary."""

    query: str
    chunk_token_length: int
    max_number_of_summaries: int
    max_token_length: int
    selected_model: str
    selected_model: str
    system_role: str
