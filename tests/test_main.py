"""Test main.py."""
import pytest
from src.main import (
    get_metadata_from_reddit_json,
    get_body_contents,
    concatenate_bodies,
)


def test_get_metadata_from_reddit_json():
    """Test get_metadata_from_reddit_json()."""
    # Test correct output
    data = {
        0: {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Test Title",
                            "selftext": "Test Selftext",
                        }
                    }
                ]
            }
        }
    }
    expected_output = ("Test Title", "Test Selftext")
    assert get_metadata_from_reddit_json(data) == expected_output

    # Test ValueError raised when title not found
    data = {
        0: {"data": {"children": [{"data": {"selftext": "Test Selftext"}}]}}
    }
    with pytest.raises(ValueError):
        get_metadata_from_reddit_json(data)

    # Test ValueError raised when selftext not found
    data = {0: {"data": {"children": [{"data": {"title": "Test Title"}}]}}}
    with pytest.raises(ValueError):
        get_metadata_from_reddit_json(data)


def test_get_body_contents():
    """Test get_body_contents()."""
    # Test correct output with list as input
    data = [
        {"key1": "value1", "key2": "value2", "body": "Test Body"},
        {"key3": "value3", "key4": "value4", "body": "Test Body 2"},
    ]
    expected_output = [("0", "Test Body"), ("1", "Test Body 2")]
    assert list(get_body_contents(data, [])) == expected_output

    # Test correct output with dictionary as input
    data = {
        "key1": "value1",
        "key2": {"key3": {"key4": "value4", "body": "Test Body"}},
    }
    expected_output = [("key2/key3", "Test Body")]
    assert list(get_body_contents(data, [])) == expected_output


def test_concatenate_bodies():
    """Test concatenate_bodies()."""
    # Test correct output
    contents = [
        ("path1", "Test Body 1"),
        ("path2", "Test Body 2"),
        ("path3", "Test Body 3"),
    ]
    expected_output = ["Test Body 1\nTest Body 2\nTest Body 3\n"]
    assert concatenate_bodies(contents) == expected_output

    # Test correct output when bodies are longer than MAX_CHUNK_SIZE tokens
    # TODO: Implement this test

    # Test correct output when no bodies are present
    contents = []
    expected_output = []
    assert concatenate_bodies(contents) == expected_output

    # Test correct output when only one body is present
    contents = [("path1", "Test Body 1")]
    expected_output = ["Test Body 1\n"]
    assert concatenate_bodies(contents) == expected_output
