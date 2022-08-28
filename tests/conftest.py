import sys
from os.path import abspath, join, dirname
project_root = abspath(dirname(dirname(__file__)))
sys.path.insert(0, project_root)

import pytest
from tests.helpers import utils


@pytest.fixture()
def app_environment():
    utils.set_project_environment()


@pytest.fixture
def app(app_environment):
    from src import create_app
    app = create_app()
    return app
