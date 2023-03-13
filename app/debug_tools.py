"""Debugging tools."""
# debugger.py
import logging
from typing import Any

import debugpy  # type: ignore


class Debugger:
    """Class to handle debugging tools for Streamlit."""

    _debugger_set_up = False

    @classmethod
    def setup_debugpy(
        cls,
        streamlit: Any,
        logger: logging.Logger,
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

            if (
                flag
                and not streamlit.session_state.debugging
                and not cls._debugger_set_up
            ):
                if not debugpy.is_client_connected():
                    # Check if the port is already in use
                    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # result = sock.connect_ex((host, port))
                    # if result == 0:
                    #     # Port is in use - kill the process
                    #     logger.warning(
                    #         f"Port {port} is already in use. Killing the process..."
                    #     )
                    #     sock.close()
                    debugpy.listen((host, port))
                if wait_for_client:
                    logger.info(">>> Waiting for debug client attach... <<<")
                    debugpy.wait_for_client()
                    logger.info(">>> ...attached! <<<")

                if streamlit.session_state.debugging is None:
                    logger.info(
                        ">>> Remote debugging activated (host=%s, port=%s) <<<",
                        host,
                        port,
                    )
                streamlit.session_state.debugging = True

                cls._debugger_set_up = True

            if not flag:
                if streamlit.session_state.debugging is None:
                    logger.info(">>> Remote debugging is NOT active <<<")
                streamlit.session_state.debugging = False
        except (ConnectionError, ValueError, TypeError) as error:
            logger.exception(f"Debugger setup failed with error: {error}")
            streamlit.exception(error)
