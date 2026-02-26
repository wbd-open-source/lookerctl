import pytest
from unittest.mock import Mock, patch
import looker_sdk

# Assuming the script is saved as looker_permissions.py
from src.lookerctl.lib.permission.create_permission_set import get_existing_permission_set

def test_get_existing_permission_set_found(mocker):
    """
    Tests that get_existing_permission_set correctly identifies and returns a permission set 
    when it exists within the Looker environment.

    This test ensures that the function returns a non-None result for an existing permission set,
    and the returned permission set's name matches the expected value.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Asserts that the function returns a valid permission set object.
        Asserts that the name of the permission set returned matches the expected name.
    """
    # Setup mock environment
    mock_permission_set = mocker.Mock()
    mock_permission_set.name = "Test_Project_Test_Permission_Set"

    mock_sdk = mocker.MagicMock()
    mock_sdk.all_permission_sets.return_value = [mock_permission_set]

    # Test function
    result = get_existing_permission_set(mock_sdk, "Test_Project_Test_Permission_Set")

    # Assertions
    assert result is not None  # nosec B101
    assert result.name == "Test_Project_Test_Permission_Set"  # nosec B101

def test_get_existing_permission_set_not_found(mocker):
    """
    Verifies that get_existing_permission_set returns None when the permission set does not exist.

    This test checks the function's ability to return None when no permission sets
    with the specified name are found in the Looker environment.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Asserts that the function returns None for a non-existent permission set.
    """
    # Mock SDK to return an empty list, simulating no permission sets found
    mock_sdk = mocker.MagicMock()
    mock_sdk.all_permission_sets.return_value = []

    # Test function
    result = get_existing_permission_set(mock_sdk, "Test_Project_Nonexistent_Permission_Set")

    # Assertion
    assert result is None  # nosec B101
