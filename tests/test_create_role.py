import pytest
from src.lookerctl.lib.role.create_role import create_role
import looker_sdk

def test_create_role_success(mocker):
    """
    Tests successful creation of a role using the Looker SDK.

    This test ensures that when the Looker SDK's `create_role` function is called,
    it is invoked exactly once with the correct parameters, simulating a successful API call
    to create a role.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Asserts that the create_role function in the SDK is called exactly once.
        Asserts that the create_role function is called with the expected parameters.
    """
    # Setup mock environment
    mock_sdk = mocker.MagicMock()
    mock_role_data = {"name": "new_role", "permission_set_id": 1, "model_set_id": 2}
    mock_sdk.create_role.return_value = mocker.Mock(name="new_role")

    # Call the function under test
    create_role(mock_sdk, mock_role_data)

    # Assert that create_role was called correctly
    mock_sdk.create_role.assert_called_once_with(body=mock_role_data)

def test_create_role_sdk_error(mocker, capsys):
    """
    Tests error handling in the create_role function when the Looker SDK throws an SDKError.

    This test checks if create_role properly handles and logs an error when the Looker SDK
    raises an SDKError during role creation, simulating an API failure.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.
        capsys (pytest.fixture): Pytest's built-in fixture that captures stdout and stderr.

    Asserts:
        Asserts that the correct error message is output to stdout.
    """
    # Setup mock SDK to throw an SDKError
    mock_sdk = mocker.MagicMock()
    mock_role_data = {"name": "new_role", "permission_set_id": 1, "model_set_id": 2}
    mock_sdk.create_role.side_effect = looker_sdk.error.SDKError("API Error")

    # Call the function under test expecting it to handle an error
    create_role(mock_sdk, mock_role_data)

    # Capture and assert on stdout output
    captured = capsys.readouterr()
    assert "API Error" in captured.out  # nosec B101
