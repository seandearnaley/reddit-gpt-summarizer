""" This module contains the settings UI for the app. """
import streamlit as st
from config import (
    ANTHROPIC_AI_MODELS,
    OPEN_AI_CHAT_MODELS,
    OPEN_AI_INSTRUCT_MODELS,
    ConfigLoader,
)
from data_types.summary import GenerateSettings
from utils.streamlit_decorators import expander_decorator

config = ConfigLoader.get_config()


def model_selection(col):
    """Render the model selection and return the selected model and settings."""
    model_configs = {
        "OpenAI Chat": OPEN_AI_CHAT_MODELS,
        "OpenAI Instruct": OPEN_AI_INSTRUCT_MODELS,
        "Anthropic": ANTHROPIC_AI_MODELS,
    }

    selected_model_config = col.radio(
        label="Select Model Config",
        options=list(model_configs.keys()),
    )

    if selected_model_config is None:
        col.text("Select a model config")
        st.stop()

    models = model_configs[selected_model_config]
    model_ids_sorted = [model.get("id") for model in models]

    selected_model = col.radio(
        label="Select Model",
        options=model_ids_sorted,
        index=0,
    )

    if selected_model is None:
        col.text("Select a model")
        st.stop()

    col.text(f"You selected model {selected_model}. Here are the parameters:")
    selected_model_details = next(
        (model for model in models if model["id"] == selected_model), None
    )

    if selected_model_details is None:
        col.text("Invalid model selected")
        st.stop()

    chunk_token_length = col.number_input(
        label="Chunk Token Length",
        value=selected_model_details["default_chunk_token_length"],
        step=1,
    )
    max_number_of_summaries = col.number_input(
        label="Max Number of Summaries",
        value=selected_model_details["default_number_of_summaries"],
        min_value=1,
        max_value=10,
        step=1,
    )
    max_token_length = col.number_input(
        label="Max Token Length",
        value=selected_model_details["max_token_length"],
        step=1,
    )

    return selected_model, chunk_token_length, max_number_of_summaries, max_token_length


@expander_decorator("Edit Settings")
def render_settings() -> GenerateSettings:
    """
    Render the settings for the app and return the model and settings.
    """

    system_role: str = st.text_input("System Role", config["DEFAULT_SYSTEM_ROLE"])
    query_text: str = st.text_area(
        "Instructions", config["DEFAULT_QUERY_TEXT"], height=250
    )

    col1, col2 = st.columns(2)

    (
        selected_model,
        chunk_token_length,
        max_number_of_summaries,
        max_token_length,
    ) = model_selection(col1)

    with col2:
        st.markdown(config["HELP_TEXT"])

    return {
        "system_role": system_role,
        "query": query_text,
        "chunk_token_length": int(chunk_token_length),
        "max_number_of_summaries": int(max_number_of_summaries),
        "max_token_length": int(max_token_length),
        "selected_model": selected_model,
    }
