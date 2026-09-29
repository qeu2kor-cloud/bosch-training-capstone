---
name: vehicle-speed-review
description: "Review the vehicle speed compliance project end-to-end. Use when checking README, docs, Flask API, domain logic, tests, and project consistency before sign-off or handoff."
---

# Vehicle Speed Compliance Review

Use this skill to review the full project for correctness, consistency, and readiness. The goal is to confirm that the code, documentation, and tests describe the same behavior and that the repository is ready for a beginner-friendly walkthrough or handoff.

## What this skill checks

- Business rules in the core checker logic
- HTTP API behavior and validation semantics
- Documentation accuracy across README and docs
- Test coverage and alignment with the requirements
- Repository readiness for local execution and validation

## Review workflow

### 1. Establish scope

Start by identifying the project boundaries:
- source code under `src/vehicle_speed_checker/`
- tests under `tests/`
- project docs under `docs/` and `README.md`
- project metadata under `pyproject.toml` and `setup.py`

### 2. Read the public overview

Review the top-level guidance first:
- `README.md`
- `docs/code-flow.md`
- `docs/swdd.md`
- `docs/unit-test-case-design.md`

Confirm the intended behavior is clear:
- SAFE when speed is below the limit
- AT_LIMIT when equal to the limit
- OVER_SPEED when above the limit
- invalid inputs are rejected consistently

### 3. Trace the implementation

Inspect the actual code path in order:
1. `src/vehicle_speed_checker/checker.py`
2. `src/vehicle_speed_checker/api.py`
3. any package entry points such as `__init__.py` and `__main__.py`

Confirm that:
- `check_compliance()` owns the business rules
- validation is centralized and consistent
- `Decimal` is used for comparison
- invalid values raise `ValidationError`
- API layer only handles HTTP concerns and JSON conversion

### 4. Validate against requirements

Check the following for consistency:
- acceptable values and valid partitions
- boundary values 79, 80, and 81
- zero as a valid value
- invalid inputs such as negative numbers, nulls, empty strings, whitespace strings, boolean values, non-numeric text, and non-finite values
- HTTP 200 for valid requests and HTTP 400 for invalid requests

### 5. Review the tests

Inspect the test files:
- `tests/test_checker.py`
- `tests/test_api.py`

Confirm that tests cover:
- successful status outcomes
- boundary behaviors
- invalid request handling
- malformed and incomplete JSON bodies
- core logic without starting a real server

### 6. Run real verification

When appropriate, run the relevant tests from the project root:

```powershell
python -m pytest tests/test_checker.py
python -m pytest tests/test_api.py
python -m pytest
```

Use the real output to validate the repository, not assumptions. If Python is missing in the environment, report that as a blocker instead of claiming success.

### 7. Compare docs to code

Look for mismatches such as:
- documented behavior that is not implemented
- code paths that are not described in docs
- test assumptions that do not match actual validation rules
- stale examples or unclear request/response payloads

### 8. Produce a review result

Return a concise review with:
- project readiness summary
- verified behavior
- any mismatches or gaps found
- recommended fixes or documentation updates
- next actions for a beginner or handoff review

## Decision points

- If code and tests agree, report as consistent and note the evidence.
- If docs describe behavior not implemented, highlight the mismatch and suggest exact doc/code fixes.
- If tests are missing a boundary case or invalid input case, flag the gap and recommend the coverage to add.
- If environment setup is unclear or broken, capture the blocker and outline the exact setup commands.

## Completion checklist

A review is complete when all of the following are true:

- README and docs match actual implementation
- API and domain behavior are traceable in code
- validation rules are consistent and documented
- tests cover success and invalid-input flows
- relevant pytest commands can be run successfully in the project environment
- review notes include clear follow-up actions if any gaps remain

## Example prompts

- Review this project for consistency between the docs and the actual Flask API.
- Check whether the code matches the behavior described in the README and code-flow document.
- Find missing or weak test coverage in the vehicle speed checker project.
- Validate that the API returns the correct HTTP status and JSON payloads for valid and invalid inputs.
- Prepare a beginner review summary for this project and highlight any gaps before handoff.

## Related customizations

- A `README-review` skill for validating project documentation quality
- A `test-gap-analysis` skill for finding missing pytest cases
- A `project-setup-check` skill for verifying Python, Flask, and local environment readiness
- A `docs-accuracy-audit` skill for checking code-to-doc alignment
