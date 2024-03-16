"""Handler for the LLM app."""

from config import ANTHROPIC_AI_TYPE
from data_types.summary import GenerateSettings
from log_tools import Logger
from pyrate_limiter import Duration, Limiter, RequestRate
from services.anthropic_connector import complete_anthropic_text
from services.openai_connector import complete_openai_text
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

    selected_model_type = settings["selected_model_type"]

    is_anthropic = selected_model_type == ANTHROPIC_AI_TYPE

    try:
        limiter.ratelimit("complete_text")

        # delegate to the appropriate completion method

        if is_anthropic:
            return complete_anthropic_text(
                prompt=prompt,
                max_tokens=max_tokens,
                settings=settings,
            )

        return complete_openai_text(
            prompt=prompt,
            max_tokens=max_tokens,
            settings=settings,
        )

    except Exception as exc:  # pylint: disable=broad-except
        app_logger.error("Error completing text: %s", exc)
        return f"Error completing text: {exc}"
