"""Test main.py."""
import pytest
from config import get_config
from services.generate_data import (
    get_comment_bodies,
    get_metadata_from_reddit_json,
    group_bodies_into_chunks,
)

DEFAULT_CHUNK_TOKEN_LENGTH = get_config()["DEFAULT_CHUNK_TOKEN_LENGTH"]


def test_get_metadata_from_reddit_json() -> None:
    """Test get_metadata_from_reddit_json()."""
    # Test correct output
    data = [
        {
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
    ]
    expected_output = ("Test Title", "Test Selftext")
    assert get_metadata_from_reddit_json(data) == expected_output

    # Test ValueError raised when title not found
    data = [{"data": {"children": [{"data": {"selftext": "Test Selftext"}}]}}]
    with pytest.raises(ValueError):
        get_metadata_from_reddit_json(data)

    # Test ValueError raised when selftext not found
    data = [{"data": {"children": [{"data": {"title": "Test Title"}}]}}]
    with pytest.raises(ValueError):
        get_metadata_from_reddit_json(data)


def test_get_comment_bodies():
    """Test get_comment_bodies()."""
    # Test correct output with dictionary as input
    data = {
        "list": [
            {"key1": "value1", "author": "author 1", "body": "Test Body"},
            {"key3": "value3", "author": "author 2", "body": "Test Body 2"},
        ]
    }
    expected_output = [
        ("list/0", "[author 1] Test Body"),
        ("list/1", "[author 2] Test Body 2"),
    ]
    assert list(get_comment_bodies(data, [])) == expected_output

    # Test correct output with dictionary as input
    data = {
        "key1": "value1",
        "key2": {"key3": {"author": "author 1", "body": "Test Body"}},
    }
    expected_output = [("key2/key3", "[author 1] Test Body")]
    assert list(get_comment_bodies(data, [])) == expected_output


def test_group_bodies_into_chunks() -> None:
    """Test group_bodies_into_chunks()."""
    # Test correct output
    contents = [
        ("path1", "Test Body 1"),
        ("path2", "Test Body 2"),
        ("path3", "Test Body 3"),
    ]
    expected_output = ["Test Body 1\nTest Body 2\nTest Body 3\n"]
    assert (
        group_bodies_into_chunks(contents, DEFAULT_CHUNK_TOKEN_LENGTH)
        == expected_output
    )

    # Test correct output when bodies are longer than MAX_CHUNK_SIZE tokens

    # Test correct output when no bodies are present
    contents = []
    expected_output = []
    assert (
        group_bodies_into_chunks(contents, DEFAULT_CHUNK_TOKEN_LENGTH)
        == expected_output
    )

    # Test correct output when only one body is present
    contents = [("path1", "Test Body 1")]
    expected_output = ["Test Body 1\n"]
    assert (
        group_bodies_into_chunks(contents, DEFAULT_CHUNK_TOKEN_LENGTH)
        == expected_output
    )
    # Test correct output when only one body is present
    contents = [("path1", "Test Body 1")]
    expected_output = ["Test Body 1\n"]
    assert (
        group_bodies_into_chunks(contents, DEFAULT_CHUNK_TOKEN_LENGTH)
        == expected_output
    )
