# test_lookertools.py

import pytest
from src.lookerctl.lib.user_attribute.create_user_attributes import get_existing_user_attribute, create_user_attribute
import looker_sdk
from looker_sdk.error import SDKError


def test_get_existing_user_attribute_found(mocker):
    """
    Tests that get_existing_user_attribute correctly retrieves an existing user attribute.

    This test simulates a scenario where the specified user attribute exists in Looker,
    ensuring that the function correctly identifies and returns the existing attribute.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the returned attribute matches the mock attribute.
    """
    # Setup mock environment
    mock_sdk = mocker.MagicMock()
    mock_attribute = mocker.Mock()
    mock_attribute.name = "test_attribute"
    mock_sdk.all_user_attributes.return_value = [mock_attribute]

    # Call the function
    result = get_existing_user_attribute(mock_sdk, "test_attribute")

    # Assertions
    assert result == mock_attribute, "The returned attribute should match the mock attribute"  # nosec B101


def test_get_existing_user_attribute_not_found(mocker):
    """
    Tests that get_existing_user_attribute returns None when the user attribute does not exist.

    This test verifies that the function correctly handles cases where no matching
    user attributes are found in the Looker environment.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the function returns None when the attribute is not found.
    """
    # Setup mock SDK to return an empty list, simulating no matching attributes
    mock_sdk = mocker.MagicMock()
    mock_sdk.all_user_attributes.return_value = []

    # Test function and assert result
    assert get_existing_user_attribute(mock_sdk, "nonexistent_attribute") is None  # nosec B101


def test_create_user_attribute_success(mocker):
    """
    Tests the successful creation of a new user attribute in Looker.

    This test ensures that create_user_attribute calls the Looker SDK to create a user attribute
    and correctly returns the created attribute object.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the function returns the expected user attribute object.
    """
    # Setup mock SDK and attribute data
    mock_sdk = mocker.MagicMock()
    attribute_data = {
        "name": "new_attribute",
        "label": "New Attribute",
        "type": "string",
        "default_value": "default",
        "value_is_hidden": False,
        "user_can_view": True,
        "user_can_edit": False
    }

    # Mock expected return value
    mock_attribute = mocker.Mock(name="prefix_new_attribute")
    mock_sdk.create_user_attribute.return_value = mock_attribute

    # Call the function and assert result
    assert create_user_attribute(mock_sdk, attribute_data, "prefix") == mock_attribute  # nosec B101
