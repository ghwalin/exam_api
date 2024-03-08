import pytest

from app import create_app

def mock_token():
    return True

@pytest.fixture()
def app():
    app = create_app()
    yield app


@pytest.fixture()
def client(app):
    app.testing = True
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()