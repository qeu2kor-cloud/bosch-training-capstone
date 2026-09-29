---
name: project-setup-check
description: "Validate the local environment and setup flow for the vehicle speed project. Use when checking Python availability, dependency installation, test execution readiness, and beginner onboarding steps."
---

# Project Setup Check

Use this skill to verify that the vehicle speed project can be set up and run correctly in a fresh local environment. This is especially useful for beginners, onboarding, or debugging why the project cannot run or test successfully.

## Goal

Ensure that a new environment can install dependencies and run the project without hidden assumptions or missing runtime tools.

## Review workflow

### 1. Confirm the runtime and tooling

Check whether the machine has the required tools:
- Python interpreter
- pip or package installation support
- a working shell such as PowerShell
- optional virtual environment support

Look for common blockers:
- `python` resolves to the Windows Store alias instead of an actual interpreter
- no environment is active
- `flask` or `pytest` is not installed
- required libraries are missing

### 2. Read the project setup guidance

Review:
- `README.md`
- `pyproject.toml`
- `setup.py`

Confirm the intended install flow:
- create or activate a virtual environment
- install the project in editable mode
- install test dependencies
- run pytest from the project root

### 3. Review packaging configuration

Check the project metadata in `pyproject.toml`:
- Python requirement is `>=3.9`
- Flask is a required dependency
- pytest is available as an optional test dependency

Confirm the install command matches the declared dependencies.

### 4. Validate the local install path

Use the real environment and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-build-isolation -e ".[test]"
```

If installation fails, diagnose the cause instead of assuming tool availability.

### 5. Check whether the app runs locally

Run the app with the proper entry point:

```powershell
flask --app vehicle_speed_checker.api run --debug
```

Then confirm the server is available on:

```text
http://127.0.0.1:5000
```

### 6. Check whether tests run successfully

Use the actual command from the repo:

```powershell
python -m pytest
```

If the environment is missing Python or dependencies, report the blocker clearly and do not claim success.

### 7. Summarize onboarding readiness

Return a short environment status with:
- Python availability
- dependency installation status
- whether tests run
- blocker details if setup failed
- exact commands to fix the environment

## Decision points

- If Python is missing or points to the Microsoft Store alias, document the fix path and tell the user to install a real interpreter.
- If the environment works but the package is not installed, guide them to install the editable package.
- If the app runs but tests fail, report the failing tests and whether the problem is code, config, or environment.
- If everything is ready, note the verified setup path for onboarding.

## Completion checklist

A setup review is complete when all are true:

- Python is available and valid for the project
- dependencies install cleanly
- the package is installed in editable mode or equivalent local setup
- tests run successfully from the repo root
- the app can start locally for a basic check
- any missing prerequisite is clearly documented

## Example prompts

- Check whether this project can run in a fresh local environment.
- Diagnose why Python or Flask is not available on this machine.
- Validate the installation and test setup for the vehicle speed project.
- Verify whether the project can be started locally and the API can be called.
- Produce a beginner onboarding checklist for running this project.

## Related customizations

- `vehicle-speed-review` for full project consistency review
- `vehicle-speed-test-review` for coverage and validation review
- `docs-accuracy-audit` for checking documentation correctness
