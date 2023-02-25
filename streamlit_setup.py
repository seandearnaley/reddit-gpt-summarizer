"""
utils for setting up streamlit
"""
# Import necessary modules
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import streamlit as st

F = TypeVar("F", bound=Callable[..., Any])


def log_with_streamlit(
    streamlit: Any = st,
) -> Callable[[F], F]:
    """Decorator to write function calls and return values to a Streamlit widget."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            streamlit.write(f"{func.__name__} returned {result}")
            return result

        return cast(F, wrapper)

    return decorator


# Set page configuration
st.set_page_config(
    page_title="Reddit Thread GPT Summarizer", page_icon="🤖", layout="wide"
)
