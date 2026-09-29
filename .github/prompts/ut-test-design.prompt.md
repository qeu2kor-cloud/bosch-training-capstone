## Role

Act as a Python and pytest unit-test designer.

## Goal

Create comprehensive, maintainable tests for the vehicle speed compliance API.

## Scope

Test the Flask `POST /check` endpoint through the application test client. Do not
start a live server and do not test external services.

## Required coverage

Cover the following successful business cases:

- Vehicle speed below the limit returns `SAFE`.
- Vehicle speed equal to the limit returns `AT_LIMIT`.
- Vehicle speed above the limit returns `OVER_SPEED`.
- Boundary values `79`, `80`, and `81` with a speed limit of `80`.
- Zero as a valid speed value.

Cover the following invalid-input cases:

- Negative vehicle speed.
- Negative speed limit.
- `null` values.
- Missing fields.
- Empty and whitespace-only values.
- Non-numeric values such as `"abc"`.
- Boolean values.
- Non-finite numeric values where supported by the request format.
- Malformed JSON or a request body that is not a JSON object.

## Assertions

For every test, assert the HTTP status code and the complete JSON response. Valid
requests must return HTTP 200 with a `status` field. Invalid requests must return
HTTP 400 with an `error` field identifying the invalid request.

## Constraints

- Use pytest and Flask's test client.
- Keep tests deterministic, isolated, and independent of network access, files,
  databases, credentials, or external services.
- Use parameterization for cases that share the same expected behavior.
- Do not duplicate business logic in the tests.
- Follow the existing project style and public API.

## Deliverables

1. A concise test-case matrix listing inputs, expected status codes, and expected
	JSON responses.
2. Executable tests in `tests/test_api.py`.
3. A short coverage summary mapping the tests to the API requirements.

## Verification

Run:

```powershell
python -m pytest tests/test_api.py
```

Confirm that all tests pass and that no test requires a running Flask server or
external service.