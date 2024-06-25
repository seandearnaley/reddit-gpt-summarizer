"""LiteLLM Connector."""

import os
from typing import Any

from config import ConfigVars
from data_types.summary import GenerateSettings
from env import EnvVarsLoader
from litellm import completion
from litellm.types.utils import ModelResponse
from log_tools import Logger

config = ConfigVars()
app_logger = Logger.get_app_logger()
env_vars = EnvVarsLoader.load_env()

# openai.organization = env_vars["OPENAI_ORG_ID"]

os.environ["OPENAI_API_KEY"] = env_vars["OPENAI_API_KEY"]
os.environ["ANTHROPIC_API_KEY"] = env_vars["ANTHROPIC_API_KEY"]
os.environ["GEMINI_API_KEY"] = env_vars["GEMINI_API_KEY"]


@Logger.log
def complete_litellm_text(
    prompt: str,
    max_tokens: int,
    settings: GenerateSettings,
) -> str:
    try:
        common_args = {
            "model": settings["selected_model"],
            "max_tokens": max_tokens,
        }

        response = completion(
            **common_args,
            messages=[
                {"role": "system", "content": settings["system_role"]},
                {"role": "user", "content": prompt},
            ],
        )

        print("response=", response)

        if isinstance(response, ModelResponse):
            if response.choices and len(response.choices) > 0:
                choice: Any = response.choices[0]
                if hasattr(choice, "message"):
                    return (
                        choice.message.content.strip() if choice.message.content else ""
                    )
                elif hasattr(choice, "text"):
                    return choice.text.strip() if choice.text else ""
        elif isinstance(response, dict):
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"].strip()
                elif "text" in choice:
                    return choice["text"].strip()

        return "Unable to extract content from the response."

    except ValueError as err:
        return f"Value error: {err}"
    except Exception as err:
        return f"Error: {err}"
