"""Logging configuration for the project."""

import logging
import logging.config
import os
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any, TypeVar

from config import ConfigVars

T = TypeVar("T")


class Logger:
    """Class to handle logging configuration."""

    _config = ConfigVars()

    _log_name = _config.LOG_NAME
    _log_file_path = os.path.abspath(_config.LOG_FILE_PATH)

    # Create the directory for log files if it doesn't exist
    if not os.path.exists(os.path.dirname(_log_file_path)):
        os.makedirs(os.path.dirname(_log_file_path))
    _logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "color": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname)s:%(message)s",
                "log_colors": _config.LOG_COLORS,
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "color",
                "filename": _log_file_path,
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "color",
            },
        },
        "loggers": {
            _log_name: {
                "handlers": ["file", "console"],
                "level": logging.INFO,
            },
        },
    }

    # Load the logging configuration using dictConfig
    try:
        logging.config.dictConfig(_logging_config)
    except ValueError as e:
        print(f"Error occurred during logging configuration: {e!s}")
        raise

    app_logger = logging.getLogger(_log_name)
    app_logger.debug("Logging is configured.")

    @classmethod
    def log(
        cls, func: Callable[..., T], logger: logging.Logger | None = None,
    ) -> Callable[..., T]:
        """Decorator to log function calls and return values."""
        if logger is None:
            logger = cls.app_logger

        @wraps(func)  # preserve the metadata of the decorated function.
        def wrapper(*args: Any, **kwargs: Any) -> T:
            logging.info("Calling %s", func.__name__)
            result = func(*args, **kwargs)
            timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if logger:
                logger.info("%s: %s returned %s", timestamp, func.__name__, result)
            return result

        return wrapper

    @classmethod
    def get_app_logger(cls) -> logging.Logger:
        """Class method to access the app_logger attribute."""
        return cls.app_logger
