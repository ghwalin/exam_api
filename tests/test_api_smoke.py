"""
Light smoke tests for the Flask endpoints, through the test client.

These are deliberately not a full acceptance suite - that's what
features/*.feature (run with `behave`) is for. This file exists so
`pytest --cov` also exercises the service/ layer and catches wiring
mistakes (wrong route, wrong decorator order, ...).

author: Marcel Suter
"""
import pytest

EXISTING_EXAM_UUID = 'a2222222-2222-2222-2222-222222222222'
EXISTING_EVENT_UUID = 'e1111111-1111-1111-1111-111111111111'


def test_login_without_a_token_is_rejected(client):
    assert client.get('/login').status_code == 401


def test_protected_endpoint_without_a_token_is_rejected(client):
    assert client.get(f'/event/{EXISTING_EVENT_UUID}').status_code == 401


def test_get_an_existing_exam(client, auth_header):
    response = client.get(
        f'/exam/{EXISTING_EXAM_UUID}',
        headers=auth_header('t.teacher@example.test', 'teacher'),
    )
    assert response.status_code == 200
    assert response.get_json(force=True)['module'] == 'M200'


def test_get_a_missing_exam_returns_404(client, auth_header):
    response = client.get(
        '/exam/00000000-0000-0000-0000-000000000000',
        headers=auth_header('t.teacher@example.test', 'teacher'),
    )
    assert response.status_code == 404


def test_a_teacher_can_create_an_exam(client, auth_header):
    response = client.post(
        '/exam',
        headers=auth_header('t.teacher@example.test', 'teacher'),
        data={
            'student': 's.student@example.test',
            'teacher': 't.teacher@example.test',
            'module': 'M400',
            'missed': '2026-11-01',
        },
    )
    assert response.status_code == 201


def test_a_student_cannot_create_an_exam(client, auth_header):
    response = client.post(
        '/exam',
        headers=auth_header('s.student@example.test', 'student'),
        data={'student': 's.student@example.test', 'teacher': 't.teacher@example.test'},
    )
    assert response.status_code == 401


def test_get_an_existing_event(client, auth_header):
    response = client.get(
        f'/event/{EXISTING_EVENT_UUID}',
        headers=auth_header('t.teacher@example.test', 'teacher'),
    )
    assert response.status_code == 200
    assert response.get_json(force=True)['status'] == 'open'


def test_people_list_requires_a_teacher(client, auth_header):
    response = client.get(
        '/people/sam/student',
        headers=auth_header('s.student@example.test', 'student'),
    )
    assert response.status_code == 401


@pytest.mark.xfail(
    reason="PersonService is registered at '/person' (app.py) with no "
           "<email> path segment, but PersonService.get(self, email) "
           "requires one, so calling this endpoint raises a TypeError "
           "instead of returning a response.",
    strict=True,
    raises=TypeError,
)
def test_get_person_endpoint_is_missing_its_url_segment(client, auth_header):
    client.get('/person', headers=auth_header('t.teacher@example.test', 'teacher'))
