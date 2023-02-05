"""Test utils.py."""
import os
from reddit_gpt_summarizer.utils import (
    get_token_length,
    request_json_from_url,
    download_parse_reddit_thread,
    generate_filename,
    save_output,
)

from reddit_gpt_summarizer.main import REDDIT_URL as TEST_URL

# Test data
TEST_TITLE = "Test Title"
TEST_JSON = {"key": "value"}
TEST_OUTPUT = "Test Output"

# Mocks
def mock_get_token_length(text):
    """Mock function to return the number of words in the given text"""
    return len(text.split())


def mock_download_parse_reddit_thread():
    """Mock function to return the test output"""
    return TEST_OUTPUT


def mock_request_json_from_url():
    """Mock function to return the test json"""
    return TEST_JSON


def test_get_token_length():
    """Test that get_token_length() returns the correct number of tokens."""
    text = "This is a test sentence."
    assert get_token_length(text) == 6


def test_download_parse_reddit_thread():
    """Test that download_parse_reddit_thread() returns a string."""
    soup = download_parse_reddit_thread(TEST_URL)
    assert isinstance(soup, str)


def test_request_json_from_url():
    """Test that request_json_from_url() returns a dictionary."""
    json_response = request_json_from_url(TEST_URL)
    assert isinstance(json_response, dict)


# Test generate_filename
def test_generate_filename():
    """Test the generate_filename function"""
    title = "Test Title with Special Characters and Spaces!"
    expected_output = "Test_Title_with_Special_Characters_and_Spaces"
    assert generate_filename(title) == expected_output


# Test save_output
def test_save_output():
    """Test the save_output function"""
    output_file_path = save_output(TEST_TITLE, TEST_OUTPUT)
    assert os.path.isfile(output_file_path)
    with open(output_file_path, "r", encoding="utf-8") as file:
        assert file.read() == TEST_OUTPUT
    os.remove(output_file_path)
    assert not os.path.isfile(output_file_path)
