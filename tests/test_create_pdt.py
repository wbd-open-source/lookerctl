import pytest
from unittest.mock import MagicMock
from looker_sdk.error import SDKError
from src.lookerctl.lib.pdt.start_pdt import trigger_pdt_build


@pytest.fixture
def sdk_mock():
    """
    Provides a mock Looker SDK with start_pdt_build method.
    """
    sdk = MagicMock()
    sdk.start_pdt_build = MagicMock()
    return sdk


def test_trigger_pdt_build_success(sdk_mock):
    """
    Test successful PDT trigger.
    """
    mock_response = {'status': 'triggered'}
    sdk_mock.start_pdt_build.return_value = mock_response

    response = trigger_pdt_build(sdk_mock, 'model1', 'view1')

    sdk_mock.start_pdt_build.assert_called_once_with(
        model_name='model1',
        view_name='view1',
        workspace='dev',
        force_rebuild=False,
        force_full_incremental=False
    )
    assert response == mock_response  # nosec B101
