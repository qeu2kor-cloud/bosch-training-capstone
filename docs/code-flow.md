# Vehicle Speed Checker: Code Flow

This document explains how a request moves through the Vehicle Speed Compliance Checker, from PowerShell or another HTTP client to the final response.

## 1. Project structure

```text
bosch-training/
|-- pyproject.toml
|-- setup.py
|-- README.md
|-- .github/workflows/tests.yml
|-- src/
|   `-- vehicle_speed_checker/
|       |-- __init__.py
|       |-- __main__.py
|       |-- api.py
|       `-- checker.py
`-- tests/
    |-- test_api.py
    `-- test_checker.py
```

| File | Responsibility |
|---|---|
| `checker.py` | Contains the business rules, validation, status values, and comparison logic. |
| `api.py` | Provides the Flask application and `POST /check` endpoint. |
| `__init__.py` | Exports the public checker API. |
| `__main__.py` | Allows the package to start the Flask development server with `python -m vehicle_speed_checker`. |
| `test_checker.py` | Tests the core business behavior directly. |
| `test_api.py` | Tests HTTP requests and responses through Flask's test client. |
| `pyproject.toml` and `setup.py` | Define package metadata and dependencies. |
| `.github/workflows/tests.yml` | Runs pytest in GitHub Actions. |

## 2. Starting the application

From the project root:

```powershell
cd C:\Users\qeu2kor\Desktop\info\bosch-training
conda activate base
flask --app vehicle_speed_checker.api run --debug
```

Flask imports `vehicle_speed_checker.api`. The module creates the application through `create_app()` and exposes it as the module-level variable `app`:

```python
app = create_app()
```

The server listens at:

```text
http://127.0.0.1:5000
```

The `--debug` option enables automatic reload and the Flask debugger. It is intended for local development only.

## 3. Request flow

A valid client request looks like this:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/check `
  -ContentType "application/json" `
  -Body '{"vehicle_speed":79,"speed_limit":80}'
```

The complete flow is:

```text
HTTP POST /check
        |
        v
Flask receives the request
        |
        v
request.get_json(silent=True)
        |
        +-- body is not a JSON object -> HTTP 400
        |
        v
Read vehicle_speed and speed_limit
        |
        v
check_compliance(vehicle_speed, speed_limit)
        |
        v
Validate and convert both values to Decimal
        |
        +-- invalid value -> ValidationError -> HTTP 400
        |
        v
Compare vehicle speed with speed limit
        |
        +-- speed < limit -> SAFE
        +-- speed == limit -> AT_LIMIT
        +-- speed > limit -> OVER_SPEED
        |
        v
Return JSON response with HTTP 200
```

## 4. API layer: `api.py`

The endpoint is registered with:

```python
@app.post("/check")
def check_speed():
```

### Step 1: Parse JSON

```python
payload = request.get_json(silent=True)
```

`silent=True` prevents Flask from raising a parsing exception for malformed JSON. If parsing fails, `payload` is `None`.

The endpoint then requires a JSON object:

```python
if not isinstance(payload, dict):
    return jsonify(error="Request body must be a JSON object"), 400
```

Examples rejected at this step:

```json
{"vehicle_speed":abc,"speed_limit":80}
```

This is invalid JSON because `abc` is not quoted. It produces:

```json
{"error":"Request body must be a JSON object"}
```

The following is valid JSON and continues to the business layer:

```json
{"vehicle_speed":"abc","speed_limit":80}
```

### Step 2: Read input fields

```python
status = check_compliance(
    payload.get("vehicle_speed"),
    payload.get("speed_limit"),
)
```

Using `.get()` means missing fields become `None`. The core validation layer then returns a consistent validation error.

### Step 3: Handle validation errors

```python
except ValidationError as error:
    return jsonify(error=str(error)), 400
```

The API deliberately returns HTTP 400 because the client supplied invalid input. The response is JSON so callers can process the error consistently.

### Step 4: Return a successful result

```python
return jsonify(status=status.value), 200
```

The `ComplianceStatus` enum value is converted to a JSON string.

## 5. Core layer: `checker.py`

The public function is:

```python
def check_compliance(vehicle_speed, speed_limit):
```

It accepts numbers and numeric strings, which is useful because HTTP request values may arrive as strings.

### Validation flow

Both inputs pass through `_to_non_negative_decimal`:

```python
speed = _to_non_negative_decimal(vehicle_speed, "vehicle_speed")
limit = _to_non_negative_decimal(speed_limit, "speed_limit")
```

The helper rejects:

- `None`
- Boolean values such as `True` and `False`
- Empty strings
- Whitespace-only strings
- Non-numeric values such as `"abc"`
- Negative values
- Non-finite values such as `NaN` and infinity

Valid values are converted to `Decimal`. Decimal comparison avoids common floating-point precision problems.

All validation failures use the same exception type:

```python
ValidationError("vehicle_speed must be a non-negative number")
```

or:

```python
ValidationError("speed_limit must be a non-negative number")
```

Zero is valid because the requirement defines the valid partition as starting at zero.

## 6. Business-rule flow

After validation, the two `Decimal` values are compared:

```python
if speed < limit:
    return ComplianceStatus.SAFE
if speed == limit:
    return ComplianceStatus.AT_LIMIT
return ComplianceStatus.OVER_SPEED
```

| Vehicle speed | Speed limit | Result |
|---:|---:|---|
| 79 | 80 | `SAFE` |
| 80 | 80 | `AT_LIMIT` |
| 81 | 80 | `OVER_SPEED` |
| 0 | 0 | `AT_LIMIT` |

The possible statuses are defined by `ComplianceStatus`:

```python
class ComplianceStatus(str, Enum):
    SAFE = "SAFE"
    AT_LIMIT = "AT_LIMIT"
    OVER_SPEED = "OVER_SPEED"
```

## 7. Response examples

### Safe

Request:

```json
{"vehicle_speed":79,"speed_limit":80}
```

Response: HTTP 200

```json
{"status":"SAFE"}
```

### At the limit

Request:

```json
{"vehicle_speed":80,"speed_limit":80}
```

Response: HTTP 200

```json
{"status":"AT_LIMIT"}
```

### Over speed

Request:

```json
{"vehicle_speed":81,"speed_limit":80}
```

Response: HTTP 200

```json
{"status":"OVER_SPEED"}
```

### Invalid value

Request:

```json
{"vehicle_speed":-1,"speed_limit":80}
```

Response: HTTP 400

```json
{"error":"vehicle_speed must be a non-negative number"}
```

PowerShell treats HTTP 400 as an exception. To print the JSON error body:

```powershell
try {
    Invoke-RestMethod -Method Post `
      -Uri http://127.0.0.1:5000/check `
      -ContentType "application/json" `
      -Body '{"vehicle_speed":-1,"speed_limit":80}'
}
catch {
    $_.ErrorDetails.Message
}
```

## 8. Test flow

Run all tests from the project root:

```powershell
python -m pytest
```

### Core tests

`tests/test_checker.py` calls `check_compliance` directly. It verifies:

- 79 versus 80 returns `SAFE`
- 80 versus 80 returns `AT_LIMIT`
- 81 versus 80 returns `OVER_SPEED`
- Zero is accepted
- Numeric strings are accepted
- Negative, null, empty, whitespace, boolean, and text inputs raise `ValidationError`

### API tests

`tests/test_api.py` creates the Flask app with `create_app()` and uses Flask's test client. It verifies:

- A valid request returns HTTP 200 and a status
- Negative, null, and text values return HTTP 400
- Missing, non-object, or malformed request bodies return HTTP 400

The API tests do not start a real server. They test the endpoint in memory, which makes them fast and repeatable.

## 9. CI flow

GitHub Actions uses `.github/workflows/tests.yml`:

```text
Push or pull request
        |
        v
Checkout repository
        |
        v
Install Python 3.9, 3.10, 3.11, and 3.12
        |
        v
Install project and test dependencies
        |
        v
Run python -m pytest
        |
        v
Workflow passes only when all tests pass
```

Testing across multiple Python versions helps detect compatibility problems early.

## 10. End-to-end example

1. Start the Flask server.
2. Send `vehicle_speed=79` and `speed_limit=80`.
3. Flask routes the request to `/check`.
4. The API extracts both fields.
5. The checker converts them to `Decimal`.
6. The checker evaluates `79 < 80`.
7. The checker returns `ComplianceStatus.SAFE`.
8. The API serializes the enum value as `SAFE`.
9. The client receives HTTP 200 and `{"status":"SAFE"}`.

For `vehicle_speed=-1`, steps 5 and 6 change: validation fails, `ValidationError` is caught by the API, and the client receives HTTP 400 with an error message.
