"""
Unit tests for data/PersonDAO.py, against the isolated fixtures in
tests/fixtures/people.json (see conftest.py: app_ctx/data_dir).

author: Marcel Suter
"""
from data.PersonDAO import PersonDAO


def test_read_person_returns_a_known_person(app_ctx):
    person = PersonDAO().read_person('t.teacher@example.test')
    assert person.firstname == 'Tina'
    assert person.role == 'teacher'


def test_read_person_lookup_is_case_insensitive(app_ctx):
    person = PersonDAO().read_person('T.TEACHER@EXAMPLE.TEST')
    assert person.email == 't.teacher@example.test'


def test_read_person_returns_a_placeholder_for_an_unknown_email(app_ctx):
    person = PersonDAO().read_person('nobody@example.test')
    assert person.firstname == '***Konto gelöscht***'
    assert person.role == 'student'


def test_filtered_list_matches_by_name_and_role(app_ctx):
    results = PersonDAO().filtered_list('sam', 'student')
    assert [p.email for p in results] == ['s.student@example.test']


def test_filtered_list_role_all_matches_any_role(app_ctx):
    results = PersonDAO().filtered_list('', 'all')
    assert {p.email for p in results} == {'t.teacher@example.test', 's.student@example.test'}


def test_filtered_list_returns_nothing_for_a_non_matching_name(app_ctx):
    assert PersonDAO().filtered_list('nobody', 'all') == []
