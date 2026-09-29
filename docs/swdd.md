# Software Design Description

## 1. Document Information

| Item | Description |
|---|---|
| System | Vehicle Speed Compliance Checker |
| Version | 0.1.0 |
| Document | Software Design Description (SWDD) |
| Runtime | Python 3.9 or newer |
| Primary framework | Flask 3.x |
| Test framework | pytest 8.x |
| Deployment scope | Local development and CI; AWS deployment is a future exercise |

## 2. Purpose and Scope

The system evaluates a vehicle speed against a configured speed limit and returns a compliance status:

- `SAFE`: vehicle speed is lower than the speed limit
- `AT_LIMIT`: vehicle speed equals the speed limit
- `OVER_SPEED`: vehicle speed is higher than the speed limit

The system also validates both input values and rejects missing, empty, non-numeric, boolean, non-finite, and negative values.

This MVP provides:

1. A reusable Python domain function.
2. A Flask HTTP API.
3. Automated unit and API tests.
4. GitHub Actions continuous integration.

The MVP does not include authentication, persistence, user management, monitoring, rate limiting, or actual AWS infrastructure.

## 3. Design Goals

- Keep business rules independent of Flask.
- Return deterministic results for the same inputs.
- Reject invalid input before comparison.
- Use clear status names defined by the requirements.
- Provide a small API that is easy to test and deploy.
- Keep the implementation suitable for training exercises across requirements, testing, development, review, CI, and deployment.

## 4. High-Level Architecture

The system uses a layered design:

```text
+-----------------------+
| Client                |
| PowerShell / HTTP     |
+-----------+-----------+
            |
            | POST /check with JSON
            v
+-----------------------+
| Flask API adapter     |
| vehicle_speed_checker |
| .api                  |
+-----------+-----------+
            |
            | calls check_compliance()
            v
+-----------------------+
| Domain logic          |
| vehicle_speed_checker |
| .checker              |
+-----------+-----------+
            |
            | status or ValidationError
            v
+-----------------------+
| JSON HTTP response    |
| 200 success / 400     |
| validation error      |
+-----------------------+
```

The API layer handles HTTP concerns. The checker layer owns validation and comparison rules. This separation allows the core logic to be tested without starting a web server and allows another adapter to be added later without changing the business rules.

## 5. Component Design

### 5.1 `checker.py`

Owns the domain model and business rules.

Public components:

```python
ComplianceStatus
ValidationError
check_compliance(vehicle_speed, speed_limit)
```

Private component:

```python
_to_non_negative_decimal(value, field_name)
```

Responsibilities:

- Define the allowed compliance statuses.
- Validate each input.
- Convert valid inputs to `Decimal`.
- Compare vehicle speed with the speed limit.
- Raise `ValidationError` for invalid input.

### 5.2 `api.py`

Owns the Flask application and HTTP contract.

Public components:

```python
create_app()
app
```

Responsibilities:

- Register `POST /check`.
- Parse JSON request bodies.
- Require a JSON object.
- Extract `vehicle_speed` and `speed_limit`.
- Delegate validation and comparison to `check_compliance`.
- Map successful results to HTTP 200 JSON.
- Map validation failures to HTTP 400 JSON.

The API does not duplicate the comparison rules.

### 5.3 `__init__.py`

Exports the core public interface:

```python
from vehicle_speed_checker import ComplianceStatus
from vehicle_speed_checker import ValidationError
from vehicle_speed_checker import check_compliance
```

### 5.4 `__main__.py`

Provides a module entry point for local execution:

```powershell
python -m vehicle_speed_checker
```

It starts the Flask development application with debug mode enabled.

### 5.5 Test components

`tests/test_checker.py` tests the domain layer directly.

`tests/test_api.py` uses Flask's test client to test the HTTP layer without opening a network port.

## 6. Data Model

The API accepts a JSON object with two fields:

```json
{
  "vehicle_speed": 79,
  "speed_limit": 80
}
```

### Input fields

| Field | Type | Required | Rules |
|---|---|---|---|
| `vehicle_speed` | number or numeric string | Yes | Must be finite and non-negative |
| `speed_limit` | number or numeric string | Yes | Must be finite and non-negative |

Missing fields are read as `None` and fail validation.

### Status model

```python
class ComplianceStatus(str, Enum):
    SAFE = "SAFE"
    AT_LIMIT = "AT_LIMIT"
    OVER_SPEED = "OVER_SPEED"
```

The enum inherits from `str` so its values can be serialized directly in JSON responses.

## 7. Input Validation Design

Both values are processed by `_to_non_negative_decimal`.

Validation sequence:

```text
Input value
    |
    +-- None or bool? -------- yes -> ValidationError
    |
    +-- empty string? -------- yes -> ValidationError
    |
    +-- Decimal conversion? -- fail -> ValidationError
    |
    +-- finite number? ------- no -> ValidationError
    |
    +-- value >= 0? ---------- no -> ValidationError
    |
    v
Return Decimal value
```

The helper uses `Decimal` rather than binary floating-point comparison. This provides predictable comparison behavior for numeric inputs.

Example validation messages:

```text
vehicle_speed must be a non-negative number
speed_limit must be a non-negative number
```

The API exposes these messages in the `error` JSON field.

## 8. Business Logic Design

After both values pass validation:

```python
if speed < limit:
    return ComplianceStatus.SAFE
if speed == limit:
    return ComplianceStatus.AT_LIMIT
return ComplianceStatus.OVER_SPEED
```

Decision table:

| Condition | Returned status |
|---|---|
| `vehicle_speed < speed_limit` | `SAFE` |
| `vehicle_speed == speed_limit` | `AT_LIMIT` |
| `vehicle_speed > speed_limit` | `OVER_SPEED` |

Boundary examples:

| Vehicle speed | Speed limit | Result |
|---:|---:|---|
| 79 | 80 | `SAFE` |
| 80 | 80 | `AT_LIMIT` |
| 81 | 80 | `OVER_SPEED` |

Zero is valid because the requirements define the valid speed partition as starting at zero.

## 9. API Contract

### Endpoint

```text
POST /check
Content-Type: application/json
```

### Successful response

Request:

```json
{"vehicle_speed":79,"speed_limit":80}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{"status":"SAFE"}
```

### Validation response

Request:

```json
{"vehicle_speed":-1,"speed_limit":80}
```

Response:

```http
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json
```

```json
{"error":"vehicle_speed must be a non-negative number"}
```

### Malformed or non-object request

A request body that cannot be parsed as a JSON object returns:

```json
{"error":"Request body must be a JSON object"}
```

with HTTP status 400.

Important distinction:

```json
{"vehicle_speed":abc,"speed_limit":80}
```

is malformed JSON, while:

```json
{"vehicle_speed":"abc","speed_limit":80}
```

is valid JSON containing a non-numeric value. Both are rejected, but at different stages.

## 10. Runtime Flow

1. A client sends `POST /check`.
2. Flask routes the request to `check_speed`.
3. The endpoint parses the body using `request.get_json(silent=True)`.
4. The endpoint rejects non-object bodies with HTTP 400.
5. The endpoint reads both fields.
6. `check_compliance` validates the vehicle speed.
7. `check_compliance` validates the speed limit.
8. Both values are converted to `Decimal`.
9. The values are compared using the business rules.
10. The API serializes the status as JSON and returns HTTP 200.
11. If validation fails, the API catches `ValidationError` and returns HTTP 400.

## 11. Error Handling

| Failure | Handling | HTTP status |
|---|---|---:|
| Missing vehicle speed | `ValidationError` | 400 |
| Missing speed limit | `ValidationError` | 400 |
| Negative vehicle speed | `ValidationError` | 400 |
| Negative speed limit | `ValidationError` | 400 |
| Empty input | `ValidationError` | 400 |
| Non-numeric input | `ValidationError` | 400 |
| Boolean input | `ValidationError` | 400 |
| Non-finite input | `ValidationError` | 400 |
| Malformed JSON | JSON-object validation response | 400 |
| Valid comparison | Status response | 200 |

The API currently does not expose stack traces in its JSON contract. Debugger output may still be available when the local development server is started with `--debug`; debug mode must not be used for production deployment.

## 12. Test Design

### Unit tests

The core tests cover:

- `79 / 80` -> `SAFE`
- `80 / 80` -> `AT_LIMIT`
- `81 / 80` -> `OVER_SPEED`
- Zero values
- Numeric strings
- Negative values
- `None`
- Empty strings
- Whitespace-only strings
- Non-numeric strings
- Boolean values

### API tests

The API tests cover:

- Successful status response.
- Negative vehicle speed.
- Null vehicle speed.
- Non-numeric vehicle speed.
- Non-object request bodies.
- Missing fields.

### Test command

```powershell
python -m pytest
```

### CI command

GitHub Actions installs the package and runs the same test command across Python 3.9 through 3.12.

## 13. Packaging and Deployment Design

The project uses a `src` package layout. Package metadata is defined in `pyproject.toml`, with `setup.py` retained for compatibility with older setuptools tooling.

Local installation:

```powershell
python -m pip install --no-build-isolation -e ".[test]"
```

The `--no-build-isolation` option is useful in managed environments where pip cannot authenticate while downloading build dependencies for an isolated environment.

Local server:

```powershell
flask --app vehicle_speed_checker.api run --debug
```

CI workflow:

```text
Push or pull request
    -> checkout code
    -> install Python matrix
    -> install project and test dependencies
    -> run pytest
```

Production deployment is outside the current MVP. A future deployment should use a production WSGI server, disable Flask debug mode, and provide appropriate logging, monitoring, network controls, and secret management.

## 14. Design Decisions and Trade-offs

### Framework-independent domain logic

The comparison logic does not depend on Flask. This makes it reusable from the API, command-line tools, jobs, or future services.

### Decimal conversion

`Decimal` is used for predictable numeric comparison. The trade-off is a small amount of conversion code compared with directly comparing Python floats.

### HTTP 400 for invalid input

Invalid client data is represented as HTTP 400 with a JSON error message. This gives API clients a clear distinction between successful compliance results and rejected requests.

### No persistence

The checker is stateless. It evaluates each request independently and does not store vehicle data or results. This keeps the MVP small and avoids introducing database and privacy requirements.

### No upper bound enforcement

The requirements describe `0 to 999` as a valid test partition but explicitly define invalid values as negative, null, empty, or non-numeric. The current implementation therefore accepts any finite non-negative number and does not impose an unrequested maximum.

## 15. Future Extensions

Potential future changes include:

- Add a documented maximum speed-limit policy if the business requirement confirms one.
- Add an OpenAPI specification.
- Add structured error codes in addition to human-readable messages.
- Add authentication and authorization.
- Add request logging and metrics.
- Add a production WSGI server configuration.
- Add Docker packaging.
- Deploy to AWS App Runner or EC2.
- Add integration tests against a running service.
