"""Logging configuration for the project."""
import logging

import colorlog

logger = logging.getLogger("reddit_gpt_summarizer_log")

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

# create file handler
file_handler = logging.FileHandler("./logs/log.log")

# create stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# set log level
logger.setLevel(logging.DEBUG)
