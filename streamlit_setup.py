"""
Utils for setting up Streamlit.
"""
from functools import wraps
from typing import Any, Callable

import streamlit as st

from config import APP_TITLE


def write_to_streamlit(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to write function calls and return values to a Streamlit widget."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
        except Exception as exception:
            st.write(f"Error occurred in {func.__name__}: {exception}")  # type: ignore
            raise exception

        st.write(f"{func.__name__} returned {result}")  # type: ignore
        return result

    return wrapper


# Set page configuration
st.set_page_config(page_title=APP_TITLE, page_icon="🤖", layout="wide")
