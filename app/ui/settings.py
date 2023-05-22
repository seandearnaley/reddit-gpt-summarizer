""" This module contains the settings UI for the app. """
from typing import Tuple

import streamlit as st
from config import (
    ANTHROPIC_AI_MODELS,
    ANTHROPIC_AI_TYPE,
    OPEN_AI_CHAT_MODELS,
    OPEN_AI_CHAT_TYPE,
    OPEN_AI_INSTRUCT_MODELS,
    OPEN_AI_INSTRUCT_TYPE,
    ConfigLoader,
)
from data_types.summary import GenerateSettings
from utils.streamlit_decorators import expander_decorator

config = ConfigLoader.get_config()


def model_selection(col) -> Tuple[str, str, int, int, int]:
    """Render the model selection and return the selected model and settings."""
    model_types = {
        OPEN_AI_CHAT_TYPE: OPEN_AI_CHAT_MODELS,
        OPEN_AI_INSTRUCT_TYPE: OPEN_AI_INSTRUCT_MODELS,
        ANTHROPIC_AI_TYPE: ANTHROPIC_AI_MODELS,
    }

    selected_model_type = col.radio(
        label="Select Model Type",
        options=list(model_types.keys()),
    )

    if selected_model_type is None:
        col.text("Select a model type")
        st.stop()

    models = model_types[selected_model_type]
    model_ids_sorted = [
        model.get("id") for model in sorted(models, key=lambda x: x.get("name"))
    ]
    selected_model = col.radio(
        label="Select Model",
        options=model_ids_sorted,
        index=0,
        format_func=lambda model_id: next(
            (model["name"] for model in models if model["id"] == model_id),
            None,
        ),
    )

    if selected_model is None:
        col.text("Select a model")
        st.stop()

    col.text(f"You selected model {selected_model}:")
    selected_model_config = next(
        (model for model in models if model["id"] == selected_model), None
    )

    if selected_model_config is None:
        col.text("Invalid model selected")
        st.stop()

    chunk_token_length = col.number_input(
        label="Chunk Token Length",
        value=selected_model_config["default_chunk_token_length"],
        step=1,
    )
    max_number_of_summaries = col.number_input(
        label="Max Number of Summaries",
        value=selected_model_config["default_number_of_summaries"],
        min_value=1,
        max_value=10,
        step=1,
    )
    max_token_length = col.number_input(
        label="Max Token Length",
        value=selected_model_config["max_token_length"],
        step=1,
    )

    return (
        selected_model_type,
        selected_model,
        chunk_token_length,
        max_number_of_summaries,
        max_token_length,
    )


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
        selected_model_type,
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
        "selected_model_type": selected_model_type,
    }
