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
