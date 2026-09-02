"""
Behave environment hooks for the exam_api Flask project.

Boots the real Flask application (the same `app.py` used to run the
service) once for the whole test run, then gives every scenario its own
disposable copy of the JSON data files so scenarios can create or update
exams/events without touching the developer's real data under DATAPATH
or leaking state between scenarios.

Authentication in this project normally goes through a Microsoft
Entra ID (MSAL) id-token exchange at GET /login, which needs a live
network call to Microsoft. Tests don't do that exchange; instead
`make_access_token()` below mints the same HS256 JWT that
util.authorization.make_access_token() would issue after a successful
login, using the app's own ACCESS_TOKEN_KEY. This is the token to send
as the `Authorization` header ("Bearer <token>") in scenarios.

author: Marcel Suter
"""
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta

import jwt

# features/environment.py -> project root is one level up
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
FIXTURE_FILES = ('people.json', 'exams.json', 'events.json')


def before_all(context):
    """
    Imports and configures the Flask app once for the whole run.

    Importing `app` runs create_app(), which reads the project's real
    `.env` (via app.config.from_pyfile), so behave must be run from the
    project root where that file lives - same as running the app itself.
    """
    from app import app as flask_app

    flask_app.config['TESTING'] = True
    flask_app.config['PROPAGATE_EXCEPTIONS'] = True

    context.flask_app = flask_app
    context.access_token_key = flask_app.config['ACCESS_TOKEN_KEY']
    context.refresh_token_key = flask_app.config['REFRESH_TOKEN_KEY']
    # Exposed on the context so steps can call context.make_access_token(...)
    # without needing to import this module from features/steps/.
    context.make_access_token = lambda email, role=None: make_access_token(context, email, role)


def before_scenario(context, scenario):
    """
    Points DATAPATH/OUTPUTPATH at a fresh temp copy of features/fixtures
    for the duration of a single scenario, and hands the scenario a
    Flask test client to make requests with.
    """
    data_dir = tempfile.mkdtemp(prefix='exam_api_behave_')
    for filename in FIXTURE_FILES:
        shutil.copy(os.path.join(FIXTURES_DIR, filename), os.path.join(data_dir, filename))

    context.data_dir = data_dir
    context.flask_app.config['DATAPATH'] = data_dir + os.sep
    context.flask_app.config['TEMPLATEPATH'] = os.path.join(PROJECT_ROOT, 'files', 'template') + os.sep
    context.flask_app.config['OUTPUTPATH'] = data_dir + os.sep

    context.client = context.flask_app.test_client()
    context.response = None
    context.auth_header = None


def after_scenario(context, scenario):
    shutil.rmtree(context.data_dir, ignore_errors=True)


def make_access_token(context, email, role=None):
    """
    Builds a valid HS256 access-token JWT for `email`, matching the
    shape util.authorization.make_access_token() issues after a real
    login, so scenarios can authenticate without the MSAL id-token
    exchange.

    :param context: the behave context (needs context.data_dir and
        context.access_token_key, set up in before_scenario/before_all)
    :param email: the person's email address
    :param role: overrides the role looked up from the people fixture;
        defaults to that person's role, or "student" if not found
    :return: an encoded JWT string
    """
    with open(os.path.join(context.data_dir, 'people.json'), encoding='utf-8') as f:
        people = json.load(f)
    person = next((p for p in people if p['email'].casefold() == email.casefold()), None)
    if role is None:
        role = person['role'] if person else 'student'

    return jwt.encode(
        {
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(minutes=10),
        },
        context.access_token_key,
        algorithm='HS256',
    )
