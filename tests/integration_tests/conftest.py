import pytest


@pytest.fixture
def test_client(app_environment, app):
    return app.test_client()
