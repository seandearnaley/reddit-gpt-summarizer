"""Debug tools for Streamlit."""
from typing import Any

import debugpy  # type: ignore


def setup_debugpy(
    streamlit: Any,
    logger: Any,
    flag: bool = False,
    wait_for_client: bool = False,
    host: str = "localhost",
    port: int = 8765,
):
    """
    Set the debug flag and start the debugpy server.
    """
    try:
        if "debugging" not in streamlit.session_state:
            streamlit.session_state.debugging = None

        if flag and not streamlit.session_state.debugging:
            if not debugpy.is_client_connected():
                debugpy.listen((host, port))
            if wait_for_client:
                logger.info(">>> Waiting for debug client attach... <<<")
                # Only include this line if you always want to attach the debugger
                debugpy.wait_for_client()
                logger.info(">>> ...attached! <<<")

            if streamlit.session_state.debugging is None:
                logger.info(
                    ">>> Remote debugging activated (host=%s, port=%s) <<<",
                    host,
                    port,
                )
            streamlit.session_state.debugging = True

        if not flag:
            if streamlit.session_state.debugging is None:
                logger.info(">>> Remote debugging is NOT active <<<")
            streamlit.session_state.debugging = False
    except Exception as streamlit_debug_exception:  # pylint: disable=broad-except
        streamlit.exception(streamlit_debug_exception)
