"""StreamlitDebug class."""
import logging

import debugpy  # type: ignore
import streamlit as st


class StreamlitDebug:
    """
    StreamlitDebug class.
    """

    def __init__(self):
        self._debug = False

    def set_debugpy(
        self,
        flag: bool = False,
        wait_for_client: bool = False,
        host: str = "localhost",
        port: int = 8765,
    ):
        """
        Set the debug flag and start the debugpy server.
        """
        self._debug = flag

        try:
            if "debugging" not in st.session_state:
                st.session_state.debugging = None

            if self._debug and not st.session_state.debugging:
                if not debugpy.is_client_connected():
                    debugpy.listen((host, port))
                if wait_for_client:
                    logging.info(">>> Waiting for debug client attach... <<<")
                    # Only include this line if you always want to attach the debugger
                    debugpy.wait_for_client()
                    logging.info(">>> ...attached! <<<")

                if st.session_state.debugging is None:
                    logging.info(
                        ">>> Remote debugging activated (host=%s, port=%s) <<<",
                        host,
                        port,
                    )
                st.session_state.debugging = True

            if not self._debug:
                if st.session_state.debugging is None:
                    logging.info(">>> Remote debugging is NOT active <<<")
                st.session_state.debugging = False
        except Exception:
            # Ignore... e.g. for cloud deployments
            pass
