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
    ) -> None:
        """
        Set the debug flag and start the debugpy server.

        :param streamlit: Streamlit instance to manage the session state.
        :param logger: Logger instance to log messages.
        :param flag: Debug flag to enable/disable debugging.
        :param wait_for_client: Flag to wait for the debug client to attach.
        :param host: Host for the debugpy server.
        :param port: Port for the debugpy server.
        """
        cls._initialize_debugging_state(streamlit)

        if flag:
            cls._activate_debugging(streamlit, logger, wait_for_client, host, port)
        else:
            cls._deactivate_debugging(streamlit, logger)

    @classmethod
    def _initialize_debugging_state(cls, streamlit: Any) -> None:
        if "debugging" not in streamlit.session_state:
            streamlit.session_state.debugging = None

    @classmethod
    def _activate_debugging(
        cls,
        streamlit: Any,
        logger: logging.Logger,
        wait_for_client: bool,
        host: str,
        port: int,
    ) -> None:
        if (
            not streamlit.session_state.debugging
            and not cls._debugger_set_up
            and not debugpy.is_client_connected()
        ):
            try:
                debugpy.listen((host, port))
                cls._debugger_set_up = True

                if wait_for_client:
                    logger.info(">>> Waiting for debug client attach... <<<")
                    debugpy.wait_for_client()
                    logger.info(">>> ...attached! <<<")

                if streamlit.session_state.debugging is None:
                    logger.info(
                        f">>> Remote debugging activated (host={host}, port={port}) <<<",
                    )
                streamlit.session_state.debugging = True

            except (ConnectionError, ValueError, TypeError) as error:
                logger.exception(f"Debugger setup failed with error: {error}")
                streamlit.exception(error)

    @classmethod
    def _deactivate_debugging(cls, streamlit: Any, logger: logging.Logger) -> None:
        if streamlit.session_state.debugging is None:
            logger.info(">>> Remote debugging is NOT active <<<")
        streamlit.session_state.debugging = False
