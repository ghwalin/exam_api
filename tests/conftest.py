"""
Shared pytest fixtures for the exam_api unit test suite.

These tests exercise the app's building blocks (models, DAOs, the
token_required/teacher_required decorators, and a handful of endpoints
through Flask's test client) in isolation. They complement, rather than
replace, the end-to-end BDD suite under features/ (run with `behave`).

author: Marcel Suter
"""
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta

import jwt
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
FIXTURE_FILES = ('people.json', 'exams.json', 'events.json')


@pytest.fixture(scope='session')
def flask_app():
    """
    Imports and configures the Flask app once for the whole test run.

    Importing `app` runs create_app(), which reads the project's real
    `.env` (via app.config.from_pyfile), so pytest must be run from the
    project root where that file lives - same as running the app itself.
    """
    from app import app as flask_app

    flask_app.config['TESTING'] = True
    flask_app.config['PROPAGATE_EXCEPTIONS'] = True
    return flask_app


@pytest.fixture
def data_dir(flask_app):
    """
    Points DATAPATH/OUTPUTPATH at a fresh temp copy of tests/fixtures for
    the duration of a single test, so tests never touch the developer's
    real data and can't leak state into each other.
    """
    tmp_dir = tempfile.mkdtemp(prefix='exam_api_pytest_')
    for filename in FIXTURE_FILES:
        shutil.copy(os.path.join(FIXTURES_DIR, filename), os.path.join(tmp_dir, filename))

    previous = {
        key: flask_app.config.get(key) for key in ('DATAPATH', 'TEMPLATEPATH', 'OUTPUTPATH')
    }
    flask_app.config['DATAPATH'] = tmp_dir + os.sep
    flask_app.config['TEMPLATEPATH'] = os.path.join(PROJECT_ROOT, 'files', 'template') + os.sep
    flask_app.config['OUTPUTPATH'] = tmp_dir + os.sep

    yield tmp_dir

    flask_app.config.update(previous)
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def app_ctx(flask_app, data_dir):
    """An app context with DATAPATH pointed at isolated fixtures - for
    exercising models/DAOs/decorators directly, without a request."""
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(flask_app, data_dir):
    """A Flask test client with DATAPATH pointed at isolated fixtures."""
    return flask_app.test_client()


@pytest.fixture
def access_token_key(flask_app):
    return flask_app.config['ACCESS_TOKEN_KEY']


@pytest.fixture
def auth_header(access_token_key):
    """auth_header(email, role) -> {'Authorization': 'Bearer <jwt>'} for
    the given person, without going through the real MSAL /login flow."""

    def _make(email, role):
        token = jwt.encode(
            {
                'email': email,
                'role': role,
                'exp': datetime.utcnow() + timedelta(minutes=10),
            },
            access_token_key,
            algorithm='HS256',
        )
        return {'Authorization': f'Bearer {token}'}

    return _make
