"""Test utils.py."""
import os
import sys
from json import JSONDecodeError
from typing import Any, Dict
from unittest import mock

import requests
import tiktoken
from services.openai_methods import num_tokens_from_string
from utils.common import (
    HEADERS,
    generate_filename,
    get_timestamp,
    request_json_from_url,
    save_output,
)


def test_num_tokens_from_string() -> None:
    """Test num_tokens_from_string()."""
    string: str = "Hello World!"
    encoding_name: str = "gpt2"

    tiktoken.get_encoding(encoding_name)
    result: int = num_tokens_from_string(string, encoding_name)

    assert result == 3


def test_generate_filename() -> None:
    """Test generate_filename()."""
    title: str = "Hello World!"
    expected_filename: str = "Hello_World"

    result: str = generate_filename(title)

    assert result == expected_filename


def test_request_json_from_url() -> None:
    """Test request_json_from_url()."""
    url: str = "https://www.example.com"
    data: Dict[str, Any] = {"key": "value"}

    with mock.patch.object(requests, "get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.json.return_value = data  # type: ignore
        mock_response.raise_for_status.return_value = None  # type: ignore
        mock_get.return_value.__enter__.return_value = mock_response

        result = request_json_from_url(url)

        mock_get.assert_called_once_with(url, headers=HEADERS, timeout=10)
        mock_response.raise_for_status.assert_called_once()  # type: ignore
        mock_response.json.assert_called_once()  # type: ignore

        assert result == data


def test_request_json_from_url_request_exception() -> None:
    """Test request_json_from_url() with a RequestException."""
    url: str = "https://www.example.com"

    with mock.patch.object(requests, "get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException

        with mock.patch.object(sys, "exit") as mock_exit:
            try:
                request_json_from_url(url)
            except SystemExit:
                mock_exit.assert_called_once_with(1)

            mock_get.assert_called_once_with(url, headers=HEADERS, timeout=10)


def test_request_json_from_url_json_decode_error() -> None:
    """Test request_json_from_url() with a JSONDecodeError."""
    url: str = "https://www.example.com"

    with mock.patch.object(requests, "get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.text = "mock response text"
        mock_response.json.side_effect = JSONDecodeError(  # type: ignore
            "error message", "mock response text", 1
        )
        mock_response.raise_for_status.return_value = None  # type: ignore
        mock_get.return_value.__enter__.return_value = mock_response

        with mock.patch.object(sys, "exit") as mock_exit:
            request_json_from_url(url)

            mock_get.assert_called_once_with(url, headers=HEADERS, timeout=10)
            mock_response.raise_for_status.assert_called_once()  # type: ignore
            mock_response.json.assert_called_once()  # type: ignore
            mock_exit.assert_called_once_with(1)


def test_save_output() -> None:
    """Test save_output()."""
    title: str = "test"
    output: str = "This is a test output."
    expected_filename = f"{generate_filename(title)}_{get_timestamp()}.txt"
    os.path.join("outputs", expected_filename)

    result = save_output(title, output)

    assert os.path.exists(result)
    with open(result, "r", encoding="utf-8") as fileout:
        assert fileout.read() == output
    os.remove(result)
