import pytest
from unittest.mock import patch
from src.lookerctl.lib.connections.db_connections import get_db_credentials_from_secrets


@pytest.fixture
def aws_credentials():
    """
    Provides mocked AWS credentials for use in tests.
    
    Returns:
        dict: A dictionary containing mocked AWS access key and secret access key.
    """
    return {
        "aws_access_key_id": "fake_key",
        "aws_secret_access_key": "fake_secret"
    }


@pytest.fixture
def mock_boto3_client(mocker):
    """
    Fixture to mock boto3 client used to interact with AWS services.

    Args:
        mocker (pytest.Mock): The pytest mocker fixture.

    Returns:
        MagicMock: A mock boto3 client.
    """
    mock_client = mocker.patch('boto3.client')
    return mock_client


def test_get_db_credentials_from_secrets_success(mock_boto3_client):
    """
    Tests successful retrieval of database credentials from AWS Secrets Manager.

    This test checks if the database credentials can be retrieved and correctly parsed
    when the AWS SDK returns a valid response.

    Args:
        mock_boto3_client (MagicMock): Mocked boto3 client provided by the `mock_boto3_client` fixture.

    Asserts:
        Asserts that the returned credentials match the expected dictionary.
    """
    mock_client = mock_boto3_client.return_value
    mock_client.get_secret_value.return_value = {
        'SecretString': '{"username":"admin","password":"password"}'
    }
    credentials = get_db_credentials_from_secrets(mock_client, "my_secret", "us-east-1")
    assert credentials == {"username": "admin", "password": "password"}, "Credentials should be parsed correctly"  # nosec B101


def test_get_db_credentials_from_secrets_failure(mock_boto3_client):
    """
    Tests the handling of errors during retrieval of database credentials from AWS Secrets Manager.

    This test verifies that the function correctly handles and logs exceptions, returning None
    when an error occurs during the call to the AWS SDK.

    Args:
        mock_boto3_client (MagicMock): Mocked boto3 client provided by the `mock_boto3_client` fixture.

    Asserts:
        Asserts that the function returns None when an exception is raised by the AWS SDK.
    """
    mock_client = mock_boto3_client.return_value
    mock_client.get_secret_value.side_effect = Exception("AWS SDK Error")
    credentials = get_db_credentials_from_secrets(mock_client, "my_secret", "us-east-1")
    assert credentials is None, "Should return None on error"  # nosec B101
