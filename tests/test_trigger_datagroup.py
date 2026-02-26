import pytest
import time
from unittest.mock import MagicMock
from looker_sdk.error import SDKError
from looker_sdk import models40 as mdls
from src.lookerctl.lib.datagroup.update_datagroup import (
    get_datagroup_id_by_name,
    trigger_datagroup,
    get_current_epoch_time
)  # Adjust the import as per your project structure


@pytest.fixture
def sdk_mock():
    return MagicMock()


def test_get_datagroup_id_by_name_found(sdk_mock):
    sdk_mock.all_datagroups.return_value = [
        mdls.Datagroup(id='123', name='sales_dg', model_name='sales_model'),
        mdls.Datagroup(id='456', name='marketing_dg', model_name='marketing_model')
    ]
    datagroup_id = get_datagroup_id_by_name(sdk_mock, 'sales_dg', 'sales_model')
    assert datagroup_id == '123'  # nosec B101


def test_get_datagroup_id_by_name_not_found(sdk_mock):
    sdk_mock.all_datagroups.return_value = [
        mdls.Datagroup(id='123', name='other_dg', model_name='other_model')
    ]
    datagroup_id = get_datagroup_id_by_name(sdk_mock, 'sales_dg', 'sales_model')
    assert datagroup_id is None  # nosec B101


def test_get_datagroup_id_by_name_invalid_input(sdk_mock):
    sdk_mock.all_datagroups.return_value = [
        mdls.Datagroup(id='321', name='valid_dg', model_name='valid_model')
    ]
    assert get_datagroup_id_by_name(sdk_mock, '', 'valid_model') is None  # nosec B101
    assert get_datagroup_id_by_name(sdk_mock, None, 'valid_model') is None  # nosec B101
    assert get_datagroup_id_by_name(sdk_mock, 'valid_dg', '') is None  # nosec B101
    assert get_datagroup_id_by_name(sdk_mock, 'valid_dg', None) is None  # nosec B101


def test_get_datagroup_id_by_name_sdk_error_on_all(sdk_mock):
    sdk_mock.all_datagroups.side_effect = SDKError("List failure")
    with pytest.raises(SDKError):
        get_datagroup_id_by_name(sdk_mock, 'any_dg', 'any_model')


def test_trigger_datagroup_success(sdk_mock, monkeypatch):
    sdk_mock.all_datagroups.return_value = [
        mdls.Datagroup(id='789', name='test_dg', model_name='test_model')
    ]
    monkeypatch.setattr(time, "time", lambda: 1720000000)
    sdk_mock.update_datagroup.return_value = mdls.Datagroup(id='789', name='test_dg', model_name='test_model')

    response = trigger_datagroup(sdk_mock, 'test_dg', 'test_model')
    sdk_mock.update_datagroup.assert_called_once()
    body_passed = sdk_mock.update_datagroup.call_args.kwargs['body']
    assert isinstance(body_passed, mdls.WriteDatagroup)  # nosec B101
    assert body_passed.stale_before == 1720000000  # nosec B101
    assert body_passed.triggered_at == 1720000000 - 60  # nosec B101
    assert response.id == '789'  # nosec B101


def test_trigger_datagroup_not_found(sdk_mock):
    sdk_mock.all_datagroups.return_value = []
    response = trigger_datagroup(sdk_mock, 'missing_dg', 'some_model')
    assert response is None  # nosec B101
    sdk_mock.update_datagroup.assert_not_called()


def test_trigger_datagroup_update_type_check(sdk_mock, monkeypatch):
    sdk_mock.all_datagroups.return_value = [
        mdls.Datagroup(id='321', name='type_dg', model_name='type_model')
    ]
    monkeypatch.setattr(time, "time", lambda: 1720000000)
    sdk_mock.update_datagroup.return_value = mdls.Datagroup(id='321', name='type_dg', model_name='type_model')

    trigger_datagroup(sdk_mock, 'type_dg', 'type_model')
    args = sdk_mock.update_datagroup.call_args.kwargs
    assert isinstance(args['body'], mdls.WriteDatagroup)  # nosec B101


def test_get_current_epoch_time(monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1720000123)
    assert get_current_epoch_time() == 1720000123  # nosec B101
