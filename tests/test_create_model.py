import pytest
from unittest.mock import MagicMock, call
from looker_sdk import error as sdk_error
from src.lookerctl.lib.model.models import create_model, create_models_from_yaml


@pytest.fixture
def sdk_mock():
    """
    Provides a mock for the Looker SDK.
    """
    sdk = MagicMock()
    sdk.create_lookml_model = MagicMock()
    return sdk


@pytest.fixture
def yaml_data():
    """
    Provides sample YAML data for testing.
    """
    return {
        'project': {'name': 'test_project'},
        'model': [
            {'name': 'model1', 'label': 'Test Model 1'},
            {'name': 'model2'}
        ]
    }


def test_create_model_success(sdk_mock, yaml_data):
    """
    Test successful creation of a single model.
    """
    model_name = "test_project_model1"
    label = "Test Model 1"
    create_model(sdk_mock, model_name, label, yaml_data)
    sdk_mock.create_lookml_model.assert_called_once_with({
        'name': model_name,
        'label': label,
        'project_name': yaml_data['project']['name']
    })


def test_create_models_from_yaml(sdk_mock, yaml_data):
    """
    Test creating multiple models from YAML configuration.
    """
    create_models_from_yaml(sdk_mock, yaml_data)
    expected_calls = [
        call({
            'name': 'test_project_model1',
            'label': 'Test Model 1',
            'project_name': 'test_project'
        }),
        call({
            'name': 'test_project_model2',
            'label': 'Default Label',
            'project_name': 'test_project'
        })
    ]
    sdk_mock.create_lookml_model.assert_has_calls(expected_calls, any_order=True)
