"""
Generic step definitions for exercising the exam_api Flask endpoints
through Flask's test client.

author: Marcel Suter
"""
from behave import given, when, then


# --------------------------------------------------------------------------
# Given: authentication
# --------------------------------------------------------------------------

@given('I am authenticated as the "{role}" "{email}"')
def step_authenticated_as(context, role, email):
    """Attaches a valid Authorization header for the given person."""
    token = context.make_access_token(email, role)
    context.auth_header = f'Bearer {token}'
    context.current_email = email
    context.current_role = role


@given('I am not authenticated')
def step_not_authenticated(context):
    context.auth_header = None


@given('I am authenticated with an expired token as "{email}"')
def step_authenticated_expired(context, email):
    import jwt
    from datetime import datetime, timedelta
    token = jwt.encode(
        {'email': email, 'role': 'teacher', 'exp': datetime.utcnow() - timedelta(minutes=1)},
        context.access_token_key,
        algorithm='HS256',
    )
    context.auth_header = f'Bearer {token}'


# --------------------------------------------------------------------------
# When: making requests
# --------------------------------------------------------------------------

def _headers(context):
    headers = {}
    if getattr(context, 'auth_header', None):
        headers['Authorization'] = context.auth_header
    return headers


@when('I send a "{method}" request to "{path}"')
def step_send_request(context, method, path):
    context.response = context.client.open(path, method=method.upper(), headers=_headers(context))


@when('I send a "{method}" request to "{path}" with form data:')
def step_send_request_with_form(context, method, path):
    data = {row['field']: row['value'] for row in context.table}
    context.response = context.client.open(
        path, method=method.upper(), headers=_headers(context), data=data
    )


# --------------------------------------------------------------------------
# Then: assertions
# --------------------------------------------------------------------------

@then('the response status code should be {status:d}')
def step_status_code(context, status):
    actual = context.response.status_code
    assert actual == status, (
        f'expected status {status}, got {actual}: {context.response.get_data(as_text=True)}'
    )


@then('the JSON response should have "{field}" equal to "{value}"')
def step_json_field_equals(context, field, value):
    # force=True: several endpoints (e.g. ExamService, EventService) return
    # a valid JSON body but don't set an application/json Content-Type
    # header, so Flask's default (strict) get_json() would return None.
    data = context.response.get_json(force=True)
    actual = data.get(field) if isinstance(data, dict) else None
    assert str(actual) == value, f'field "{field}" was {actual!r}, expected {value!r} in {data!r}'


@then('the JSON response array should have {count:d} item')
@then('the JSON response array should have {count:d} items')
def step_json_array_length(context, count):
    data = context.response.get_json(force=True)
    assert isinstance(data, list), f'expected a JSON array, got {data!r}'
    assert len(data) == count, f'expected {count} items, got {len(data)}: {data!r}'


@then('the response body should contain "{text}"')
def step_body_contains(context, text):
    body = context.response.get_data(as_text=True)
    assert text in body, f'expected {text!r} in response body: {body!r}'
