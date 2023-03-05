"""Data types for the application."""
from typing import List, TypedDict

SummaryData = TypedDict(
    "SummaryData",
    {
        "title": str,
        "selftext": str,
        "output": str,
        "prompts": List[str],
        "summaries": List[str],
        "groups": List[str],
    },
)


GenerateSettings = TypedDict(
    "GenerateSettings",
    {
        "query": str,
        "chunk_token_length": int,
        "number_of_summaries": int,
        "max_token_length": int,
        "selected_model": str,
    },
)
