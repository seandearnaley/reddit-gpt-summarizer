"""OpenAI Utility functions for the Reddit Scraper project."""

import anthropic
from config import ConfigLoader
from data_types.summary import GenerateSettings
from env import EnvVarsLoader
from log_tools import Logger

config = ConfigLoader.get_config()
app_logger = Logger.get_app_logger()
env_vars = EnvVarsLoader.load_env()


@Logger.log
def complete_anthropic_text(
    prompt: str,
    max_tokens: int,
    settings: GenerateSettings,
) -> str:
    """
    Use Anthropic's GPT model to complete text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.
        max_tokens (int, optional): The maximum number of tokens to generate in the
        response. Defaults to MAX_TOKENS - num_tokens_from_string(prompt).
        settings (GenerateSettings): The settings to use for generating the text.

    Returns:
        str: The completed text.
    """

    model = settings["selected_model"]

    try:
        anthropic_client = anthropic.Client(env_vars["ANTHROPIC_API_KEY"])
        response = anthropic_client.completion(
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
            stop_sequences=[anthropic.HUMAN_PROMPT],
            model=model,
            max_tokens_to_sample=max_tokens,
        )

        return response["completion"].strip()
    except Exception as err:  # pylint: disable=broad-except
        return f"error: {err}"
