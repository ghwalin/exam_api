"""
Unit tests for util/authorization.py: the token_required / teacher_required
decorators and make_access_token(), exercised directly against a Flask
request context rather than through a running endpoint.

author: Marcel Suter
"""
import jwt

from util.authorization import make_access_token, teacher_required, token_required


@token_required
def _whoami():
    from flask import g
    return g.user.email


@token_required
@teacher_required
def _teachers_only():
    return 'ok'


# --- make_access_token ---------------------------------------------------

def test_make_access_token_for_a_known_person(app_ctx):
    token, role = make_access_token('t.teacher@example.test')
    assert role == 'teacher'
    decoded = jwt.decode(token, app_ctx.config['ACCESS_TOKEN_KEY'], algorithms=['HS256'])
    assert decoded['email'] == 't.teacher@example.test'
    assert decoded['role'] == 'teacher'


def test_make_access_token_for_an_unrecognized_email_still_issues_a_token(app_ctx):
    # PersonDAO.read_person() never returns None - for an email it doesn't
    # recognize it falls back to a placeholder Person(role='student'), so
    # make_access_token()'s `if person is not None` branch (and thus its
    # (None, 'guest') result) is effectively unreachable in practice.
    token, role = make_access_token('nobody@example.test')
    assert role == 'student'
    decoded = jwt.decode(token, app_ctx.config['ACCESS_TOKEN_KEY'], algorithms=['HS256'])
    assert decoded['email'] == 'nobody@example.test'
    assert decoded['role'] == 'student'


# --- token_required --------------------------------------------------------

def test_token_required_rejects_a_missing_header(flask_app, data_dir):
    with flask_app.test_request_context('/'):
        response = _whoami()
    assert response.status_code == 401


def test_token_required_rejects_an_invalid_token(flask_app, data_dir):
    headers = {'Authorization': 'Bearer not-a-real-token'}
    with flask_app.test_request_context('/', headers=headers):
        response = _whoami()
    assert response.status_code == 401


def test_token_required_accepts_a_valid_token_and_populates_g_user(flask_app, data_dir, auth_header):
    headers = auth_header('t.teacher@example.test', 'teacher')
    with flask_app.test_request_context('/', headers=headers):
        result = _whoami()
    assert result == 't.teacher@example.test'


# --- teacher_required --------------------------------------------------

def test_teacher_required_rejects_a_student(flask_app, data_dir, auth_header):
    headers = auth_header('s.student@example.test', 'student')
    with flask_app.test_request_context('/', headers=headers):
        response = _teachers_only()
    assert response.status_code == 401


def test_teacher_required_allows_a_teacher(flask_app, data_dir, auth_header):
    headers = auth_header('t.teacher@example.test', 'teacher')
    with flask_app.test_request_context('/', headers=headers):
        result = _teachers_only()
    assert result == 'ok'
