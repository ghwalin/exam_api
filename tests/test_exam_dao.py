"""
Unit tests for data/ExamDAO.py, against the isolated fixtures in
tests/fixtures/exams.json (see conftest.py: app_ctx/data_dir).

author: Marcel Suter
"""
import pytest

from data.ExamDAO import ExamDAO
from model.Exam import Exam
from model.Person import Person

EXISTING_UUID = 'a2222222-2222-2222-2222-222222222222'


def test_read_exam_returns_an_existing_exam(app_ctx):
    exam = ExamDAO().read_exam(EXISTING_UUID)
    assert exam.module == 'M200'
    assert exam.teacher.email == 't.teacher@example.test'
    assert exam.student.email == 's.student@example.test'


def test_read_exam_returns_none_for_an_unknown_uuid(app_ctx):
    assert ExamDAO().read_exam('does-not-exist') is None


# --- status filtering ------------------------------------------------------
#
# KNOWN BUG (data/ExamDAO.py, condition()): the status-filter logic is
# broken in two ways:
#   1. `if status not in none_values: status = 'all'` runs *before* the
#      open/closed bucket checks, so it immediately overwrites any real
#      'open'/'closed' filter value back to 'all'. GET /exams?status=...
#      therefore has no actual filtering effect - every value behaves
#      like 'all'.
#   2. status=None or '' (i.e. no filter requested at all, the normal case
#      when a caller doesn't pass ?status=) is *not* in that overwrite, so
#      it falls straight into the open-bucket check with status still
#      None/'', which is not in ['open', 'all'] - so exams in the "open"
#      status codes (10/20/30/35/40) get silently excluded even though no
#      filter was requested.
# The two xfail tests below spell out the behavior a caller would
# reasonably expect; both currently fail against the real implementation.

def test_filtered_list_status_all_returns_everything(app_ctx):
    assert len(ExamDAO().filtered_list(None, None, None, 'all')) == 1


@pytest.mark.xfail(reason='see status-filtering bug note above (point 2)', strict=True)
def test_filtered_list_with_no_status_filter_should_return_everything(app_ctx):
    assert len(ExamDAO().filtered_list(None, None, None, None)) == 1


@pytest.mark.xfail(reason='see status-filtering bug note above (point 1)', strict=True)
def test_filtered_list_closed_status_should_exclude_an_open_exam(app_ctx):
    assert ExamDAO().filtered_list(None, None, None, 'closed') == []


def test_filtered_list_matches_student_by_name_or_email(app_ctx):
    dao = ExamDAO()
    assert len(dao.filtered_list('Sam', None, None, 'all')) == 1
    assert len(dao.filtered_list('nobody', None, None, 'all')) == 0


def test_update_exam_creates_a_new_exam_and_persists_it(app_ctx):
    dao = ExamDAO()
    new_exam = Exam(
        exam_uuid='new-uuid', event_uuid='e1111111-1111-1111-1111-111111111111',
        student=Person(email='s.student@example.test', firstname='Sam', lastname='Student',
                        department='IT', role='student'),
        teacher=Person(email='t.teacher@example.test', firstname='Tina', lastname='Teacher',
                        department='IT', role='teacher'),
        cohort='IT23a', module='M300', exam_num='3', missed='2026-10-05',
        duration=45, room='H200', remarks='', tools='', status='10',
    )
    dao.update_exam(new_exam)

    # load_exams() re-reads DATAPATH/exams.json - confirms the write landed
    persisted = ExamDAO().read_exam('new-uuid')
    assert persisted is not None
    assert persisted.module == 'M300'
    # Exam.to_json() always stringifies duration (`str(self.duration)`), so
    # after a save/load round trip it comes back as '45', not the int 45 -
    # matches the real exports/*.json data, which store it quoted too.
    assert persisted.duration == '45'


def test_update_exam_clears_invited_flag_when_the_event_changes(app_ctx):
    dao = ExamDAO()
    exam = dao.read_exam(EXISTING_UUID)
    exam.invited = True
    dao.update_exam(exam)

    moved = Exam(
        exam_uuid=EXISTING_UUID, event_uuid='a-different-event',
        student=None, teacher=None, cohort=None, module=None, exam_num=None,
        missed=None, duration=0, room=None, remarks=None, tools=None, status=None,
    )
    dao.update_exam(moved)

    reloaded = ExamDAO().read_exam(EXISTING_UUID)
    assert reloaded.event_uuid == 'a-different-event'
    assert reloaded.invited is False
