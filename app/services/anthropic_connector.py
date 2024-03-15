"""Anthropic Connector"""

import anthropic
from config import ConfigVars
from data_types.summary import GenerateSettings
from env import EnvVarsLoader
from log_tools import Logger

config = ConfigVars()
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
        response.
        settings (GenerateSettings): The settings to use for generating the text.

    Returns:
        str: The completed text.
    """

    try:
        anthropic_client = anthropic.Anthropic(api_key=env_vars["ANTHROPIC_API_KEY"])
        messagex = anthropic_client.messages.create(
            model=settings["selected_model"],
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt},
                # Optionally, you can add an assistant's last turn here if needed
            ],

            
        )

        # Assuming the response is a list of dictionaries with "type" and "text"
        # Extracting the text from the first item in the response list
        if message.content and isinstance(message.content, list):
            response_text = next(
                (item.text for item in message.content if item.type == "text"), ""
            )
            return response_text.strip()
        else:
            return "No response received."
    except Exception as err:  # pylint: disable=broad-except
        return f"error: {err}"
