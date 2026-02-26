import pytest
from unittest.mock import MagicMock
from looker_sdk import models40 as mdls
from src.lookerctl.lib.project.create_project import create_project
import sys
import os


sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'looker-iac', 'lib', 'project'
        )
    )
)


@pytest.fixture
def mock_sdk_and_yaml():
    sdk = MagicMock()
    sdk.update_session = MagicMock()
    sdk.create_project = MagicMock(return_value=mdls.Project(name='test_project'))

    yaml_data = {
        'project': {
            'name': 'test_project'
        }
    }

    return sdk, yaml_data
