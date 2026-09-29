# Unit Test Case Design

## 1. Purpose

This document defines unit test cases for the domain component in `src/vehicle_speed_checker/checker.py`.

The design is based on [SWDD](swdd.md), especially:

- `check_compliance(vehicle_speed, speed_limit)` is the public function under test.
- Valid inputs are finite and non-negative numbers or numeric strings.
- Invalid inputs raise `ValidationError`.
- The comparison returns `SAFE`, `AT_LIMIT`, or `OVER_SPEED`.
- Unit tests exercise the domain layer directly and do not start Flask.

## 2. Test Scope

### In scope

- Vehicle speed validation
- Speed limit validation
- Numeric conversion to `Decimal`
- Boundary comparison behavior
- Compliance status values
- Validation error type and message
- Stateless repeated execution

### Out of scope

- HTTP status codes and JSON serialization
- Flask routing and request parsing
- PowerShell behavior
- GitHub Actions execution
- AWS infrastructure

Those concerns belong to the API tests and deployment verification described in the SWDD.

## 3. Test Conditions

### Test environment

- Python 3.9 or newer
- pytest 8.x
- Project installed in the active environment

### Test command

```powershell
python -m pytest tests/test_checker.py
```

### Test oracle

The expected result is determined by the SWDD decision table:

| Condition | Expected result |
|---|---|
| `vehicle_speed < speed_limit` | `ComplianceStatus.SAFE` |
| `vehicle_speed == speed_limit` | `ComplianceStatus.AT_LIMIT` |
| `vehicle_speed > speed_limit` | `ComplianceStatus.OVER_SPEED` |

## 4. Equivalence Partitions

| Partition ID | Input class | Expected behavior |
|---|---|---|
| EP-01 | Finite non-negative number | Accepted and compared |
| EP-02 | Numeric string | Accepted and converted to `Decimal` |
| EP-03 | `None` | Raise `ValidationError` |
| EP-04 | Negative number | Raise `ValidationError` |
| EP-05 | Empty string | Raise `ValidationError` |
| EP-06 | Whitespace-only string | Raise `ValidationError` |
| EP-07 | Non-numeric string | Raise `ValidationError` |
| EP-08 | Boolean | Raise `ValidationError` |
| EP-09 | Non-finite number | Raise `ValidationError` |

The same partitions apply independently to `vehicle_speed` and `speed_limit`.

## 5. Boundary Analysis

The primary comparison boundary is the speed limit.

| Boundary case | Vehicle speed | Speed limit | Expected status |
|---|---:|---:|---|
| Just below limit | 79 | 80 | `SAFE` |
| Equal to limit | 80 | 80 | `AT_LIMIT` |
| Just above limit | 81 | 80 | `OVER_SPEED` |

The lower valid-input boundary is zero:

| Boundary case | Vehicle speed | Speed limit | Expected status |
|---|---:|---:|---|
| Minimum valid values | 0 | 0 | `AT_LIMIT` |
| Minimum speed below positive limit | 0 | 1 | `SAFE` |
| Positive speed above zero limit | 1 | 0 | `OVER_SPEED` |

The SWDD does not require a maximum of 999 to be enforced. Therefore, values above 999 are not treated as invalid unless the requirement changes.

## 6. Detailed Unit Test Cases

| ID | Objective | Vehicle speed | Speed limit | Expected result | Test type |
|---|---|---:|---:|---|---|
| UT-001 | Return safe below limit | 79 | 80 | `ComplianceStatus.SAFE` | Boundary / business rule |
| UT-002 | Return at-limit at exact boundary | 80 | 80 | `ComplianceStatus.AT_LIMIT` | Boundary / business rule |
| UT-003 | Return over-speed above limit | 81 | 80 | `ComplianceStatus.OVER_SPEED` | Boundary / business rule |
| UT-004 | Accept minimum valid values | 0 | 0 | `ComplianceStatus.AT_LIMIT` | Boundary / valid partition |
| UT-005 | Accept zero speed below positive limit | 0 | 1 | `ComplianceStatus.SAFE` | Boundary / valid partition |
| UT-006 | Compare positive speed above zero limit | 1 | 0 | `ComplianceStatus.OVER_SPEED` | Boundary / valid partition |
| UT-007 | Accept integer-like numeric strings | `"79"` | `"80"` | `ComplianceStatus.SAFE` | Equivalence partition |
| UT-008 | Accept decimal numeric strings | `"79.5"` | `"80.0"` | `ComplianceStatus.SAFE` | Equivalence partition |
| UT-009 | Reject negative vehicle speed | -1 | 80 | `ValidationError` | Invalid partition |
| UT-010 | Reject negative speed limit | 80 | -1 | `ValidationError` | Invalid partition |
| UT-011 | Reject null vehicle speed | `None` | 80 | `ValidationError` | Invalid partition |
| UT-012 | Reject null speed limit | 80 | `None` | `ValidationError` | Invalid partition |
| UT-013 | Reject empty vehicle speed | `""` | 80 | `ValidationError` | Invalid partition |
| UT-014 | Reject empty speed limit | 80 | `""` | `ValidationError` | Invalid partition |
| UT-015 | Reject whitespace vehicle speed | `"   "` | 80 | `ValidationError` | Invalid partition |
| UT-016 | Reject whitespace speed limit | 80 | `"   "` | `ValidationError` | Invalid partition |
| UT-017 | Reject non-numeric vehicle speed | `"abc"` | 80 | `ValidationError` | Invalid partition |
| UT-018 | Reject non-numeric speed limit | 80 | `"abc"` | `ValidationError` | Invalid partition |
| UT-019 | Reject boolean vehicle speed | `True` | 80 | `ValidationError` | Invalid partition |
| UT-020 | Reject boolean speed limit | 80 | `False` | `ValidationError` | Invalid partition |
| UT-021 | Reject non-finite vehicle speed | `"NaN"` | 80 | `ValidationError` | Robustness |
| UT-022 | Reject non-finite speed limit | 80 | `"Infinity"` | `ValidationError` | Robustness |
| UT-023 | Identify vehicle-speed field in error | -1 | 80 | Message contains `vehicle_speed` | Error contract |
| UT-024 | Identify speed-limit field in error | 80 | -1 | Message contains `speed_limit` | Error contract |
| UT-025 | Remain deterministic for repeated input | 79 | 80 | Same `SAFE` result each time | Statelessness |

## 7. Test Case Procedures

### UT-001: Below-limit speed

**Purpose:** Verify BR1.

**Steps:**

1. Call `check_compliance(79, 80)`.
2. Compare the returned value with `ComplianceStatus.SAFE`.

**Expected:** The function returns `ComplianceStatus.SAFE` and does not raise an exception.

### UT-002: Exact-limit speed

**Purpose:** Verify BR2.

**Steps:**

1. Call `check_compliance(80, 80)`.
2. Compare the returned value with `ComplianceStatus.AT_LIMIT`.

**Expected:** The function returns `ComplianceStatus.AT_LIMIT`.

### UT-003: Above-limit speed

**Purpose:** Verify BR3.

**Steps:**

1. Call `check_compliance(81, 80)`.
2. Compare the returned value with `ComplianceStatus.OVER_SPEED`.

**Expected:** The function returns `ComplianceStatus.OVER_SPEED`.

### UT-009: Negative vehicle speed

**Purpose:** Verify invalid speed input is rejected.

**Steps:**

1. Call `check_compliance(-1, 80)`.
2. Assert that `ValidationError` is raised.
3. Assert that the message identifies `vehicle_speed`.

**Expected:** No status is returned.

### UT-017: Non-numeric vehicle speed

**Purpose:** Verify text input is rejected by the domain layer.

**Steps:**

1. Call `check_compliance("abc", 80)`.
2. Assert that `ValidationError` is raised.

**Expected:** No status is returned and the error identifies `vehicle_speed`.

## 8. Pytest Mapping

The current implementation can cover the design using parameterized tests:

```python
@pytest.mark.parametrize(
    ("vehicle_speed", "speed_limit", "expected"),
    [
        (79, 80, ComplianceStatus.SAFE),
        (80, 80, ComplianceStatus.AT_LIMIT),
        (81, 80, ComplianceStatus.OVER_SPEED),
    ],
)
def test_check_compliance_returns_expected_status(
    vehicle_speed, speed_limit, expected
):
    assert check_compliance(vehicle_speed, speed_limit) is expected
```

Invalid partitions can be grouped because they share the same expected exception:

```python
@pytest.mark.parametrize(
    ("vehicle_speed", "speed_limit"),
    [
        (-1, 80),
        (80, -1),
        (None, 80),
        (80, None),
        ("", 80),
        (80, ""),
        ("abc", 80),
        (80, "abc"),
        ("   ", 80),
        (True, 80),
    ],
)
def test_check_compliance_rejects_invalid_inputs(vehicle_speed, speed_limit):
    with pytest.raises(ValidationError):
        check_compliance(vehicle_speed, speed_limit)
```

## 9. Traceability Matrix

| Requirement/design rule | Covered by test cases |
|---|---|
| `vehicle_speed < speed_limit` -> `SAFE` | UT-001, UT-005, UT-007, UT-008 |
| `vehicle_speed == speed_limit` -> `AT_LIMIT` | UT-002, UT-004 |
| `vehicle_speed > speed_limit` -> `OVER_SPEED` | UT-003, UT-006 |
| Reject negative vehicle speed | UT-009 |
| Reject negative speed limit | UT-010 |
| Reject missing/null values | UT-011, UT-012 |
| Reject empty values | UT-013, UT-014 |
| Reject whitespace-only values | UT-015, UT-016 |
| Reject non-numeric values | UT-017, UT-018 |
| Reject booleans | UT-019, UT-020 |
| Reject non-finite values | UT-021, UT-022 |
| Identify invalid field in error | UT-023, UT-024 |
| Deterministic stateless behavior | UT-025 |

## 10. Entry and Exit Criteria

### Entry criteria

- The domain function is implemented.
- `ComplianceStatus` and `ValidationError` are importable.
- Test dependencies are installed.
- The test environment uses Python 3.9 or newer.

### Exit criteria

- All planned unit tests pass.
- Every status branch is covered.
- Every validation partition is covered.
- The traceability matrix has no uncovered design rule.
- No test depends on the Flask server or external services.
