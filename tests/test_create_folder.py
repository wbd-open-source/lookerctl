import pytest
from looker_sdk.error import SDKError
from src.lookerctl.lib.folders.final_create import get_content_metadata_id, create_folders, update_folder_permissions

def test_get_content_metadata_id_success(mocker):
    """
    Tests successful retrieval of a folder's content metadata ID from Looker.
    
    Ensures that when the Looker SDK correctly returns a folder object, the function
    extracts and returns the content metadata ID successfully.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the returned content metadata ID is correct as per the mocked data.
    """
    mock_sdk = mocker.MagicMock()
    mock_folder = mocker.Mock(content_metadata_id=123)
    mock_sdk.folder.return_value = mock_folder
    result = get_content_metadata_id(mock_sdk, "folder123")
    assert result == 123  # nosec B101

def test_get_content_metadata_id_failure(mocker):
    """
    Tests the behavior of get_content_metadata_id when the SDK raises an SDKError.

    Verifies that the function returns None when an error occurs during the folder
    retrieval process due to SDK issues.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the function returns None in case of retrieval errors.
    """
    mock_sdk = mocker.MagicMock()
    mock_sdk.folder.side_effect = SDKError("Failed to retrieve folder")
    result = get_content_metadata_id(mock_sdk, "folder123")
    assert result is None  # nosec B101

def test_create_folders_success(mocker):
    """
    Tests the successful creation of a folder in Looker.

    This test checks if the folder creation function can correctly create a folder and return
    the folder's ID and content metadata ID when the SDK call is successful.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that the folder ID and metadata ID are correctly returned from the mocked SDK response.
    """
    mock_sdk = mocker.MagicMock()
    mock_folder = mocker.Mock(id="new_folder123", content_metadata_id=321)
    mock_sdk.create_folder.return_value = mock_folder
    folder_id, metadata_id = create_folders(mock_sdk, "parent123", "New Folder")
    assert folder_id == "new_folder123"  # nosec B101
    assert metadata_id == 321  # nosec B101

def test_create_folders_failure(mocker):
    """
    Tests folder creation error handling in the Looker SDK.

    Checks if create_folders returns None for both folder ID and metadata ID when
    an exception occurs during the folder creation process.

    Args:
        mocker (pytest.fixture): Pytest's mocker fixture to mock dependencies.

    Asserts:
        Assert that both folder ID and metadata ID are None when the creation fails due to SDK errors.
    """
    mock_sdk = mocker.MagicMock()
    mock_sdk.create_folder.side_effect = SDKError("Creation failed")
    folder_id, metadata_id = create_folders(mock_sdk, "parent123", "New Folder")
    assert folder_id is None  # nosec B101
    assert metadata_id is None  # nosec B101
