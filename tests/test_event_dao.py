"""
Unit tests for data/EventDAO.py, against the isolated fixtures in
tests/fixtures/events.json (see conftest.py: app_ctx/data_dir).

author: Marcel Suter
"""
import pytest

from data.EventDAO import EventDAO

EXISTING_UUID = 'e1111111-1111-1111-1111-111111111111'


def test_read_event_returns_an_existing_event(app_ctx):
    event = EventDAO().read_event(EXISTING_UUID)
    assert event.status == 'open'
    assert event.rooms == ['H100']


def test_read_event_returns_none_for_an_unknown_uuid(app_ctx):
    assert EventDAO().read_event('does-not-exist') is None


def test_filtered_list_with_no_date_returns_all_events(app_ctx):
    assert len(EventDAO().filtered_list(None)) == 1


@pytest.mark.xfail(
    reason="EventDAO.filtered_list() (data/EventDAO.py) calls "
           "event.timestamp.date(), but Event.timestamp is a plain str, not "
           "a datetime, so filtering by date raises AttributeError. Also "
           "reproduced by the @known-issue scenarios in features/event.feature.",
    strict=True,
    raises=AttributeError,
)
def test_filtered_list_with_a_matching_date(app_ctx):
    assert len(EventDAO().filtered_list('2026-11-05')) == 1


def test_update_event_changes_the_status_and_persists_it(app_ctx):
    assert EventDAO().update_event(EXISTING_UUID, 'closed') is True
    assert EventDAO().read_event(EXISTING_UUID).status == 'closed'


def test_update_event_returns_false_for_an_unknown_uuid(app_ctx):
    assert EventDAO().update_event('does-not-exist', 'closed') is False
