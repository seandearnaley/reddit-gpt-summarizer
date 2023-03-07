"""
This module contains tools for Streamlit.
"""
# Import necessary modules


from functools import wraps
from typing import Any, Callable

import streamlit as st


def error_to_streamlit(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to write function calls and return values to a Streamlit widget."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
        except Exception as exception:
            st.write(f"Error occurred in {func.__name__}: {exception}")  # type: ignore
            raise exception

        # st.write(f"{func.__name__} returned {result}")  # type: ignore
        return result

    return wrapper


def expander_decorator(
    title: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to wrap a function with st.expander.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with st.expander(title):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def spinner_decorator(title: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to wrap a function with st.spinner.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with st.spinner(title):
                return func(*args, **kwargs)

        return wrapper

    return decorator