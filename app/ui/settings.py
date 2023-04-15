"""
UI functions for settings
"""
# Import necessary modules


import streamlit as st
from config import ConfigLoader
from data_types.summary import GenerateSettings
from services.openai_methods import get_models
from utils.streamlit_decorators import expander_decorator

config = ConfigLoader.get_config()


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
    with col1:
        models = get_models()
        model_ids = [model["id"] for model in models]  # type: ignore
        print("model_ids", model_ids)
        filtered_list = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-4",
            "gpt-4-0314",
            # "gpt-4-32k",
            # "gpt-4-32k-0314",
        ]
        model_ids_sorted = sorted(filtered_list)
        default_model_index = model_ids_sorted.index(config["DEFAULT_GPT_MODEL"])
        selected_model = st.radio(
            label="Select Model",
            options=model_ids_sorted,
            index=default_model_index,
        )

        if selected_model:
            st.text(f"You selected model {selected_model}. Here are the parameters:")
            st.text(models[model_ids.index(selected_model)])  # type: ignore
        else:
            st.text("Select a model")
            st.stop()

        chunk_token_length = st.number_input(
            label="Chunk Token Length",
            value=config["DEFAULT_CHUNK_TOKEN_LENGTH"],
            step=1,
        )

        max_number_of_summaries = st.number_input(
            label="Max Number of Summaries",
            value=config["DEFAULT_NUMBER_OF_SUMMARIES"],
            min_value=1,
            max_value=10,
            step=1,
        )

        max_token_length = st.number_input(
            label="Max Token Length",
            value=config["DEFAULT_MAX_TOKEN_LENGTH"],
            step=1,
        )
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
