"""Test utils.py."""

import os

import tiktoken
from utils.common import generate_filename, get_timestamp, save_output
from utils.llm_utils import num_tokens_from_string


def test_num_tokens_from_string() -> None:
    """Test num_tokens_from_string()."""
    string: str = "Hello World!"
    encoding_name: str = "gpt2"

    tiktoken.get_encoding(encoding_name)
    result: int = num_tokens_from_string(string)

    assert result == 3


def test_generate_filename() -> None:
    """Test generate_filename()."""
    title: str = "Hello World!"
    expected_filename: str = "Hello_World"

    result: str = generate_filename(title)

    assert result == expected_filename


def test_save_output() -> None:
    """Test save_output()."""
    title: str = "test"
    output: str = "This is a test output."
    expected_filename = f"{generate_filename(title)}_{get_timestamp()}.txt"
    os.path.join("outputs", expected_filename)

    result = save_output(title, output)

    assert os.path.exists(result)
    with open(result, encoding="utf-8") as fileout:
        assert fileout.read() == output
    os.remove(result)
