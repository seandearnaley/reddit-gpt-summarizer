"""Data types for the application."""
from typing import List, TypedDict


class SummaryData(TypedDict):
    """Data for a summary."""

    title: str
    selftext: str
    output: str
    prompts: List[str]
    summaries: List[str]
    groups: List[str]


class GenerateSettings(TypedDict):
    """Settings for generating a summary."""

    query: str
    chunk_token_length: int
    max_number_of_summaries: int
    max_token_length: int
    selected_model: str
    selected_model: str
    system_role: str
