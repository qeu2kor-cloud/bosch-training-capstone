import pytest

from vehicle_speed_checker import ComplianceStatus, ValidationError, check_compliance


@pytest.mark.parametrize(
    ("vehicle_speed", "speed_limit", "expected"),
    [
        (79, 80, ComplianceStatus.SAFE),
        (80, 80, ComplianceStatus.AT_LIMIT),
        (81, 80, ComplianceStatus.OVER_SPEED),
        (0, 0, ComplianceStatus.AT_LIMIT),
        ("79", "80", ComplianceStatus.SAFE),
    ],
)
def test_check_compliance_returns_expected_status(vehicle_speed, speed_limit, expected):
    assert check_compliance(vehicle_speed, speed_limit) is expected


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
