"""Test utils.py."""
import os
import sys
import json
from unittest import mock
import requests
import tiktoken
from reddit_gpt_summarizer.utils import (
    num_tokens_from_string,
    request_json_from_url,
    generate_filename,
    save_output,
)


def test_num_tokens_from_string():
    """Test num_tokens_from_string()."""
    string = "Hello World!"
    encoding_name = "gpt2"

    with mock.patch.object(tiktoken, "get_encoding") as mock_get_encoding:
        encoding = mock.MagicMock()
        mock_get_encoding.return_value = encoding
        encoding.encode.return_value = [string]

        result = num_tokens_from_string(string, encoding_name)

        mock_get_encoding.assert_called_once_with(encoding_name)
        encoding.encode.assert_called_once_with(string)
        assert result == 1


def test_generate_filename():
    """Test generate_filename()."""
    title = "Hello World!"
    expected_filename = "Hello_World"

    result = generate_filename(title)

    assert result == expected_filename


def test_request_json_from_url():
    """Test request_json_from_url()."""
    url = "https://www.example.com"
    data = {"key": "value"}

    with mock.patch.object(requests, "get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.json.return_value = data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value.__enter__.return_value = mock_response

        result = request_json_from_url(url)

        mock_get.assert_called_once_with(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

        assert result == data


def test_request_json_from_url_request_exception():
    """Test request_json_from_url() with a RequestException."""
    url = "https://www.example.com"

    with mock.patch.object(requests, "get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException

        with mock.patch.object(sys, "exit") as mock_exit:
            try:
                request_json_from_url(url)
            except SystemExit:
                mock_exit.assert_called_once_with(1)

            mock_get.assert_called_once_with(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
            )


def test_request_json_from_url_json_decode_error():
    """Test request_json_from_url() with a JSONDecodeError."""
    url = "https://www.example.com"

    with mock.patch.object(requests, "get") as mock_get:
        mock_response = mock.MagicMock()
        mock_response.text = "mock response text"
        mock_response.json.side_effect = json.decoder.JSONDecodeError(
            "error message", "mock response text", 1
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value.__enter__.return_value = mock_response

        with mock.patch.object(sys, "exit") as mock_exit:
            request_json_from_url(url)

            mock_get.assert_called_once_with(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
            )
            mock_response.raise_for_status.assert_called_once()
            mock_response.json.assert_called_once()
            mock_exit.assert_called_once_with(1)


def test_save_output():
    """Test save_output()."""
    title = "Hello World!"
    output = "Output Content"
    timestamp = "20230205120000"

    with mock.patch.object(os, "getcwd") as mock_getcwd, mock.patch.object(
        os, "makedirs"
    ) as mock_makedirs, mock.patch("os.path.join") as mock_join, mock.patch(
        "builtins.open"
    ) as mock_open, mock.patch(
        "pathlib.Path.exists"
    ) as mock_exists, mock.patch(
        "utils.get_timestamp"
    ) as mock_get_timestamp:

        mock_get_timestamp.return_value = timestamp
        mock_getcwd.return_value = "current/working/directory"
        mock_exists.return_value = False
        mock_join.return_value = (
            "current/working/directory/outputs/Hello_World_20230205120000.txt"
        )

        save_output(title, output)

        mock_getcwd.assert_called_once()
        mock_makedirs.assert_called_once_with(
            "current/working/directory/outputs/Hello_World_20230205120000.txt",
            exist_ok=True,
        )
        # mock_join.assert_called_with(
        #     "current/working/directory/outputs/Hello_World_20230205120000.txt",
        #     "Hello_World_20230205120000.txt",
        # )
        mock_open.assert_called_once_with(
            "current/working/directory/outputs/Hello_World_20230205120000.txt",
            "w",
            encoding="utf-8",
        )
        mock_get_timestamp.assert_called_once()
