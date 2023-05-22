"""OpenAI Utility functions for the Reddit Scraper project."""


import openai
from config import OPEN_AI_CHAT_TYPE, ConfigLoader
from data_types.summary import GenerateSettings
from env import EnvVarsLoader
from log_tools import Logger
from openai.openai_object import OpenAIObject

config = ConfigLoader.get_config()
app_logger = Logger.get_app_logger()
env_vars = EnvVarsLoader.load_env()

openai.organization = env_vars["OPENAI_ORG_ID"]
openai.api_key = env_vars["OPENAI_API_KEY"]


@Logger.log
def complete_openai_text(
    prompt: str,
    max_tokens: int,
    settings: GenerateSettings,
) -> str:
    """
    Use OpenAI's GPT model to complete text based on the given prompt.

    Args:
        prompt (str): The prompt to use as the starting point for text completion.
        max_tokens (int, optional): The maximum number of tokens to generate in the
        response. Defaults to MAX_TOKENS - num_tokens_from_string(prompt).
        settings (GenerateSettings): The settings to use for generating the text.

    Returns:
        str: The completed text.
    """

    system_role, model, selected_model_type = (
        settings["system_role"],
        settings["selected_model"],
        settings["selected_model_type"],
    )

    is_chat = selected_model_type == OPEN_AI_CHAT_TYPE

    try:
        response = (
            openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                frequency_penalty=0.7,
            )
            if is_chat
            else openai.Completion.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
            )
        )

        if not isinstance(response, OpenAIObject):
            raise ValueError("Invalid Response")

        if response.choices:
            return (
                response.choices[0].message.content.strip()
                if is_chat
                else response.choices[0].text.strip()
            )

        raise ValueError("Response doesn't have choices or choices have no text.")

    except openai.OpenAIError as err:
        return f"OpenAI Error: {err}"
    except ValueError as err:
        return f"Value error: {err}"
