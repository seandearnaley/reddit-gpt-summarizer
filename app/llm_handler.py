"""Handler for the LLM app."""

from data_types.summary import GenerateSettings
from log_tools import Logger
from pyrate_limiter import Duration, Limiter, RequestRate
from services.litellm_connector import complete_litellm_text
from utils.llm_utils import validate_max_tokens
from utils.streamlit_decorators import error_to_streamlit

app_logger = Logger.get_app_logger()

rate_limits = (RequestRate(10, Duration.MINUTE),)  # 10 requests a minute

# Create the rate limiter
# Pyrate Limiter instance
limiter = Limiter(*rate_limits)


@Logger.log
@error_to_streamlit
def complete_text(
    prompt: str,
    max_tokens: int,
    settings: GenerateSettings,
) -> str:
    """LLM orchestrator"""

    validate_max_tokens(max_tokens)

    try:
        limiter.ratelimit("complete_text")

        return complete_litellm_text(
            prompt=prompt,
            max_tokens=max_tokens,
            settings=settings,
        )

    except Exception as exc:  # pylint: disable=broad-except
        app_logger.error("Error completing text: %s", exc)
        return f"Error completing text: {exc}"
