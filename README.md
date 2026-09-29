# Vehicle Speed Compliance Checker

A small Python and Flask MVP for the GitHub Copilot training exercises in `GitHub_Copilot_MVP_Requirement.md`.

For a complete explanation of the request lifecycle, validation, business rules,
API responses, tests, and CI flow, see [docs/code-flow.md](docs/code-flow.md).
The detailed software design is documented in [docs/swdd.md](docs/swdd.md).
The unit-level test cases are defined in [docs/unit-test-case-design.md](docs/unit-test-case-design.md).

## Behavior

`check_compliance(vehicle_speed, speed_limit)` returns:

- `SAFE` when vehicle speed is below the limit
- `AT_LIMIT` when vehicle speed equals the limit
- `OVER_SPEED` when vehicle speed is above the limit

Missing, empty, non-numeric, boolean, and negative values raise `ValidationError`. Zero is valid. Numeric strings are accepted so the core function can be used with form or JSON input.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-build-isolation -e ".[test]"
python -m pytest
```

If editable installation reports that `setup.py` or `setup.cfg` is missing, run the
upgrade command above inside the active environment and retry the install. The
repository also includes `setup.py` for compatibility with older setuptools-based
tools. On a managed network where pip cannot authenticate while creating an
isolated build environment, keep the `--no-build-isolation` option so pip uses the
already-installed local build tools.

## API

Start the development server:

```powershell
flask --app vehicle_speed_checker.api run --debug
```

Send a check request:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/check `
  -ContentType "application/json" `
  -Body '{"vehicle_speed":79,"speed_limit":80}'
```

The response is:

```json
{"status":"SAFE"}
```

Invalid requests return HTTP 400 with an `error` message.

PowerShell treats HTTP 400 responses as exceptions. To display the validation
response instead of the default error text, use `try/catch`:

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

The response body is:

```json
{"error":"vehicle_speed must be a non-negative number"}
```

The same HTTP 400 behavior applies to `null` and non-numeric values such as
`"abc"`, covering TC004, TC005, and TC006.

## Training scope

The implementation covers requirements analysis, test design, Python development, pytest automation, refactoring, code review, and CI. AWS deployment is intentionally left as a follow-up exercise: the Flask app can be deployed to EC2 or App Runner, but this repository does not contain AWS credentials or infrastructure resources.
