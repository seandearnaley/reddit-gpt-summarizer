"""
This module contains tools for Streamlit.
"""
# Import necessary modules

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import streamlit as st

T = TypeVar("T")


def error_to_streamlit(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to write function calls and return values to a Streamlit widget."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            result = func(*args, **kwargs)
        except Exception as exception:
            st.write(f"Error occurred in {func.__name__}: {exception}")
            raise exception

        return result

    return wrapper


def expander_decorator(
    title: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to wrap a function with st.expander.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with st.expander(title):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def spinner_decorator(title: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to wrap a function with st.spinner.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with st.spinner(title):
                return func(*args, **kwargs)

        return wrapper

    return decorator
