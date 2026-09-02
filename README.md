# exam
Manage exams for students who missed the orginal date

## Testing (Behave)

This project has a [Behave](https://behave.readthedocs.io/) BDD test suite under `features/`
that drives the Flask app through its test client - no real server, database, or MSAL login
needed.

### Setup

```bash
# from the project root, with your existing virtualenv active
pip install -r requirements-test.txt
```

### Running the tests

```bash
behave
```

Each scenario gets its own throwaway copy of `features/fixtures/*.json` (see
`features/environment.py`), so tests never touch the real data under `DATAPATH`. Since login
normally goes through a Microsoft Entra ID (MSAL) id-token exchange, scenarios authenticate by
minting an access token directly (`Given I am authenticated as the "teacher" "..."`) instead of
calling `/login`.

Two scenarios in `features/event.feature` are tagged `@known-issue`: they document a real bug
found while writing this suite (`EventDAO.filtered_list` in `data/EventDAO.py` calls
`event.timestamp.date()` on a plain string, so `GET /events/<date>` currently raises an
`AttributeError`). Run the rest of the suite without them with:

```bash
behave --tags="not @known-issue"
```

## Testing (pytest + coverage)

Alongside the Behave acceptance suite, `tests/` has a [pytest](https://docs.pytest.org/) unit
test suite for the models, DAOs and the `token_required`/`teacher_required` decorators, plus a
few smoke tests through the Flask test client. It shares the same idea as `features/`: each
test gets its own throwaway copy of `tests/fixtures/*.json`, and a `.env`-supplied
`ACCESS_TOKEN_KEY` mints tokens directly instead of going through `/login`.

### Setup

```bash
# from the project root, with your existing virtualenv active
pip install -r requirements-test.txt
```

### Running the tests

```bash
pytest
```

This also produces a coverage report (via `pytest-cov`, configured in `pytest.ini` /
`.coveragerc`): a summary in the terminal and a browsable one at `htmlcov/index.html`. Both
`.coverage` and `htmlcov/` are generated files - already covered by `.gitignore`.

A handful of tests are marked `@pytest.mark.xfail(strict=True)` - they document real bugs found
while writing this suite, rather than skipping over them:

- `tests/test_event_dao.py::test_filtered_list_with_a_matching_date` - the same `EventDAO`
  bug as the Behave `@known-issue` scenarios above.
- `tests/test_exam_dao.py` - `ExamDAO.condition()`'s status filter (`data/ExamDAO.py`) is
  broken: any real `status` value (e.g. `open`/`closed`) gets silently overwritten back to
  `all` before it's used, so `GET /exams?status=...` doesn't actually filter; and omitting the
  filter entirely (`status=None`) incorrectly excludes exams in the "open" status codes instead
  of returning everything.
- `tests/test_models.py::test_person_omitted_optional_fields_default_to_the_declared_string` -
  `Person`'s `firstname`/`lastname`/`department`/`role` fields declare a `' '` default, but a
  `@property` of the same name is defined later in the class and overwrites it. Constructing
  `Person(email=...)` without also passing those fields sets them to a `<property object>`
  instead of a string, which then blows up `Exam.to_json()` if that person is ever serialized.
- `tests/test_api_smoke.py::test_get_person_endpoint_is_missing_its_url_segment` - `app.py`
  registers `PersonService` at `/person` with no `<email>` segment, but
  `PersonService.get(self, email)` requires one, so calling it raises a `TypeError`.

If any of these get fixed, the corresponding test will unexpectedly pass (XPASS) and fail the
run (`strict=True`) as a reminder to delete the `xfail` marker.
