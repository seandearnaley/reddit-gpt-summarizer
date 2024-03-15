"""This module contains the settings UI for the app."""

from typing import Tuple

import streamlit as st
from config import (
    ANTHROPIC_AI_MODELS,
    ANTHROPIC_AI_TYPE,
    OPEN_AI_CHAT_MODELS,
    OPEN_AI_CHAT_TYPE,
    OPEN_AI_INSTRUCT_MODELS,
    OPEN_AI_INSTRUCT_TYPE,
    ConfigVars,
)
from data_types.summary import GenerateSettings
from utils.streamlit_decorators import expander_decorator

config = ConfigVars()


def model_selection(col) -> Tuple[str, str, int, int, int, int]:
    """Render the model selection and return the selected model and settings."""
    model_types = {
        OPEN_AI_CHAT_TYPE: OPEN_AI_CHAT_MODELS,
        OPEN_AI_INSTRUCT_TYPE: OPEN_AI_INSTRUCT_MODELS,
        ANTHROPIC_AI_TYPE: ANTHROPIC_AI_MODELS,
    }

    selected_model_type = col.radio(
        "Select Model Type", options=list(model_types.keys())
    )

    models = model_types[selected_model_type]
    model_ids_sorted = {
        model.id: model for model in sorted(models, key=lambda x: x.name)
    }
    selected_model = col.radio(
        "Select Model",
        options=model_ids_sorted.keys(),
        index=0,
        format_func=lambda model_id: model_ids_sorted[model_id].name,
    )

    selected_model_config = model_ids_sorted[selected_model]

    return (
        selected_model_type,
        selected_model,
        col.number_input(
            "Chunk Token Length",
            value=selected_model_config.default_chunk_token_length,
            step=1,
        ),
        col.number_input(
            "Max Number of Summaries",
            value=selected_model_config.default_number_of_summaries,
            min_value=1,
            max_value=10,
            step=1,
        ),
        col.number_input(
            "Max Token Length", value=selected_model_config.max_token_length, step=1
        ),
        col.number_input(
            "Max Context Length",
            value=getattr(selected_model_config, "max_context_length", 0),
            step=1,
        ),
    )


@expander_decorator("Edit Settings")
def render_settings() -> GenerateSettings:
    """
    Render the settings for the app and return the model and settings.
    """

    system_role: str = st.text_input("System Role", config.DEFAULT_SYSTEM_ROLE)
    query_text: str = st.text_area(
        "Instructions", config.DEFAULT_QUERY_TEXT, height=250
    )

    col1, col2 = st.columns(2)

    (
        selected_model_type,
        selected_model,
        chunk_token_length,
        max_number_of_summaries,
        max_token_length,
        max_context_length,
    ) = model_selection(col1)

    with col2:
        st.markdown(config.HELP_TEXT)

    return {
        "system_role": system_role,
        "query": query_text,
        "chunk_token_length": chunk_token_length,
        "max_number_of_summaries": max_number_of_summaries,
        "max_token_length": max_token_length,
        "selected_model": selected_model,
        "selected_model_type": selected_model_type,
        "max_context_length": max_context_length,
    }
