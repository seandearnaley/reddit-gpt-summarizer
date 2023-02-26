"""Logging configuration for the project."""
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

import colorlog

from config import LOG_NAME

F = TypeVar("F", bound=Callable[..., Any])

app_logger = logging.getLogger(LOG_NAME)

# create file handler
file_handler = logging.FileHandler("./logs/log.log")

# create stream handler
stream_handler = logging.StreamHandler()

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

stream_handler.setFormatter(formatter)
# add handlers to logger
app_logger.addHandler(file_handler)
app_logger.addHandler(stream_handler)

# set log level
app_logger.setLevel(logging.INFO)


def log_with_logging(logger: Optional[logging.Logger] = app_logger) -> Callable[[F], F]:
    """Decorator to log function calls and return values."""
    if logger is None:
        raise ValueError("logger must be provided")

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info("%s: %s returned %s", timestamp, func.__name__, result)
            return result

        return cast(F, wrapper)

    return decorator
