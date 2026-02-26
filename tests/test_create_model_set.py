import pytest
from looker_sdk import error
from unittest.mock import Mock, patch
# Import your module here, assume it's named `looker_operations`
from src.lookerctl.lib.model.model_set import create_model_set, get_existing_model_set, update_model_set

def test_get_existing_model_set_found(mocker):
    """
    Tests that get_existing_model_set successfully finds and returns a model set when it exists in Looker.

    This test simulates the condition where the model set with the specified name exists in the Looker environment,
    ensuring that the function correctly identifies and returns the model set.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the function returns a non-None result when the model set exists.
        Assert that the returned model set's name matches the expected name.
    """
    # Setup mock environment
    mock_model_set = mocker.Mock()
    mock_model_set.name = "Test_Model_Set"

    mock_sdk = mocker.MagicMock()
    mock_sdk.all_model_sets.return_value = [mock_model_set]

    # Define the name of the model set to look for
    model_set_name = "Test_Model_Set"
    # Call the function
    result = get_existing_model_set(mock_sdk, model_set_name)

    # Output the function's result for debugging
    print("Function Output:", result)
    if result:
        print("Result Name:", result.name)

    # Verify that the function found the model set
    assert result is not None, "The result should not be None"  # nosec B101
    assert result.name == model_set_name, "The model set name should match the input"  # nosec B101

def test_get_existing_model_set_not_found(mocker):
    """
    Tests that get_existing_model_set returns None when the model set does not exist.

    This test ensures that the function behaves correctly when no model sets matching the specified name
    are found in the Looker environment, by returning None.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the function returns None when the model set is not found.
    """
    # Setup mock SDK response
    mock_sdk = mocker.MagicMock()
    mock_sdk.all_model_sets.return_value = []

    # Define a non-existent model set name
    model_set_name = "Non_Existent_Model_Set"

    # Call the function
    result = get_existing_model_set(mock_sdk, model_set_name)

    # Verify that no model set is found
    assert result is None  # nosec B101


def test_create_model_set(mocker):
    """
    Tests the creation of a model set in Looker.

    This test verifies that the create_model_set function calls the Looker SDK to create a model set with the
    specified name and model list as defined in the YAML configuration data.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the Looker SDK's create_model_set method is called exactly once.
    """
    # Setup the mock SDK and the expected return value
    mock_sdk = mocker.MagicMock()
    mock_sdk.create_model_set.return_value = Mock(name="Created_Model_Set")

    # Define model set data and corresponding project data
    model_set_data = {"name": "New_Set", "models": ["model1", "model2"]}
    yaml_data = {"project": {"name": "Test_Project"}}

    # Call the function
    create_model_set(mock_sdk, model_set_data, yaml_data)

    # Check that the SDK method was called once
    mock_sdk.create_model_set.assert_called_once()
