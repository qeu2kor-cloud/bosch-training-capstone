---
name: vehicle-speed-test-review
description: "Review the vehicle speed project from a testing and validation perspective. Use when checking pytest coverage, API contract accuracy, invalid-input handling, and whether the tests match the documented requirements."
---

# Vehicle Speed Test Review

Use this skill to review the project from a testing lens. Focus on whether the code and documentation match the expected business behavior, whether the tests cover the right cases, and whether the project is ready for a beginner-friendly validation walkthrough.

## Goal

Assess whether the repository’s tests genuinely validate the behavior of the vehicle speed checker and whether the API contract is consistently implemented across documentation, code, and pytest assertions.

## Review workflow

### 1. Start with the requirement story

Read the public project docs first:
- `README.md`
- `docs/code-flow.md`
- `docs/swdd.md`
- `docs/unit-test-case-design.md`

Confirm the core expected outcomes:
- below limit -> SAFE
- equal to limit -> AT_LIMIT
- above limit -> OVER_SPEED
- invalid inputs -> HTTP 400 with an error message

### 2. Inspect the business logic

Review the implementation in:
- `src/vehicle_speed_checker/checker.py`

Check that:
- validation is centralized
- null, empty, whitespace, negative, boolean, and non-numeric inputs are rejected
- zero is accepted
- Decimal comparison is used
- exceptions are raised with useful error messages

### 3. Inspect the API contract

Review:
- `src/vehicle_speed_checker/api.py`

Confirm that:
- `POST /check` accepts a JSON object
- malformed or non-object JSON is rejected with HTTP 400
- valid requests return HTTP 200 with a JSON status field
- invalid requests return HTTP 400 with an `error` field

### 4. Review test coverage

Inspect:
- `tests/test_checker.py`
- `tests/test_api.py`

Check that the tests cover:
- SAFE vs AT_LIMIT vs OVER_SPEED
- boundary values 79, 80, 81
- zero valid input
- negative values
- empty and whitespace values
- non-numeric values
- boolean values
- malformed and missing bodies
- invalid request bodies and object shape checks

### 5. Validate the test logic itself

Look for anti-patterns and weak tests:
- tests that duplicate business logic instead of validating behavior
- assertions that check only a subset of the response
- cases missing the required status code and full JSON payload
- tests that depend on a live server instead of Flask’s test client

### 6. Run the verification commands

Use the actual environment to validate the project:

```powershell
python -m pytest tests/test_checker.py
python -m pytest tests/test_api.py
python -m pytest
```

If Python is unavailable, record that as an environment blocker and do not treat tests as passing.

### 7. Produce a testing review summary

Return:
- which scenarios are covered
- which scenarios are missing or weak
- whether the tests align to the documented requirements
- any failure or blocker found in local verification
- recommended follow-up changes

## Decision points

- If the code, tests, and docs agree: mark the behavior as aligned and cite the evidence.
- If a boundary or invalid input case is missing: flag it as test-gap coverage.
- If API tests check only status code but not the full JSON: note that the response contract is under-tested.
- If tests require a real server rather than Flask’s test client: flag it as non-isolated and not aligned with the project scope.

## Completion checklist

A testing review is complete when all are true:

- valid and invalid cases are covered
- boundary values are explicitly tested
- API contract assertions include status and JSON
- test setup is isolated and deterministic
- docs and tests describe the same expected results
- pytest can run in the project environment or the environment blocker is clearly documented

## Example prompts

- Review the test coverage for the vehicle speed API and check for missing edge cases.
- Compare the documented behavior to the actual pytest assertions in the project.
- Find any API tests that do not fully validate the response contract.
- Check whether the invalid-input tests cover all required partitions.
- Summarize the current test quality for this beginner project and highlight gaps.

## Related customizations

- `vehicle-speed-review` for full project and documentation review
- `project-setup-check` for environment verification
- `docs-accuracy-audit` for code-to-doc consistency checks
