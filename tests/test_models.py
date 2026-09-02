"""
Unit tests for the plain data model classes (model/*.py).

author: Marcel Suter
"""
import datetime
import json

import pytest

from model.Event import Event
from model.Exam import Exam
from model.Person import Person


def _make_exam(**overrides):
    # department is passed explicitly for both people - see
    # test_person_omitted_fields_default_to_a_property_object_not_a_string
    # for why leaving it out here would blow up Exam.to_json().
    teacher = Person(email='t@example.test', firstname='Tina', lastname='Teacher',
                      department='IT', role='teacher')
    student = Person(email='s@example.test', firstname='Sam', lastname='Student',
                      department='IT', role='student')
    defaults = dict(
        exam_uuid='u1', event_uuid='ev1', student=student, teacher=teacher,
        cohort='IT23a', module='M1', exam_num='1', missed='2026-09-15',
        duration=30, room='H100', remarks='', tools='', status='20',
    )
    defaults.update(overrides)
    return Exam(**defaults)


# --- Person ----------------------------------------------------------------

def test_person_fullname_combines_first_and_last_name():
    person = Person(email='a@example.test', firstname='Ada', lastname='Lovelace')
    assert person.fullname == 'Ada Lovelace'


def test_person_to_json_contains_all_fields():
    person = Person(email='a@example.test', firstname='Ada', lastname='Lovelace',
                     department='IT', role='teacher')
    data = json.loads(person.to_json())
    assert data == {
        'email': 'a@example.test',
        'firstname': 'Ada',
        'lastname': 'Lovelace',
        'fullname': 'Ada Lovelace',
        'department': 'IT',
        'role': 'teacher',
    }


def test_person_department_none_becomes_empty_string():
    person = Person(email='a@example.test', department=None)
    assert person.department == ''


@pytest.mark.xfail(
    reason="Person (model/Person.py) declares `firstname: str = ' '` (and "
           "the same for lastname/department/role) as dataclass fields, "
           "but each is immediately re-defined a few lines later as a "
           "@property with the same name. That later assignment clobbers "
           "the class attribute @dataclass captured as the field's "
           "default *before* the property existed, so the default actually "
           "stored is the property object itself, not ' '. Any caller that "
           "constructs Person(email=...) without also passing firstname/"
           "lastname/department/role gets those attributes set to a "
           "<property object>, not a string - and later code that "
           "serializes it (e.g. Exam.to_json()) blows up with "
           "'Object of type property is not JSON serializable'.",
    strict=True,
)
def test_person_omitted_optional_fields_default_to_the_declared_string():
    person = Person(email='a@example.test')
    assert person.firstname == ' '
    assert person.lastname == ' '
    assert person.department == ' '
    assert person.role == ' '


# --- Exam --------------------------------------------------------------

def test_exam_missed_parses_a_date_string():
    exam = _make_exam(missed='2026-09-15')
    assert exam.missed == datetime.datetime(2026, 9, 15)


def test_exam_missed_accepts_a_date_object_as_is():
    today = datetime.date(2026, 9, 15)
    exam = _make_exam(missed=today)
    assert exam.missed == today


def test_exam_status_text_maps_known_status_codes():
    assert _make_exam(status='20').status_text == 'offen'
    assert _make_exam(status='50').status_text == 'absolviert'


def test_exam_status_text_falls_back_to_unknown_for_unmapped_codes():
    assert _make_exam(status='999').status_text == 'unbekannt'


def test_exam_to_json_response_includes_full_person_details():
    exam = _make_exam()
    data = json.loads(exam.to_json(response=True))
    assert data['teacher']['fullname'] == 'Tina Teacher'
    assert data['student']['fullname'] == 'Sam Student'
    assert data['module'] == 'M1'


def test_exam_to_json_persisted_form_uses_email_addresses_only():
    exam = _make_exam()
    data = json.loads(exam.to_json(response=False))
    assert data['teacher'] == 't@example.test'
    assert data['student'] == 's@example.test'


# --- Event -------------------------------------------------------------

def test_event_to_json_round_trips_fields():
    event = Event(
        event_uuid='e1', timestamp='2026-01-01T10:00:00',
        rooms=['H1'], supervisors=['a@example.test'], status='open',
    )
    data = json.loads(event.to_json())
    assert data == {
        'event_uuid': 'e1',
        'timestamp': '2026-01-01T10:00:00',
        'supervisors': ['a@example.test'],
        'rooms': ['H1'],
        'status': 'open',
    }
