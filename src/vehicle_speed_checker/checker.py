from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any


class ComplianceStatus(str, Enum):
    SAFE = "SAFE"
    AT_LIMIT = "AT_LIMIT"
    OVER_SPEED = "OVER_SPEED"


class ValidationError(ValueError):
    """Raised when a speed or speed limit is missing or invalid."""


def _to_non_negative_decimal(value: Any, field_name: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValidationError(f"{field_name} must be a non-negative number")

    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"{field_name} must be a non-negative number")

    try:
        number = Decimal(str(value).strip()) if isinstance(value, str) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{field_name} must be a non-negative number") from None

    if not number.is_finite() or number < 0:
        raise ValidationError(f"{field_name} must be a non-negative number")

    return number


def check_compliance(vehicle_speed: Any, speed_limit: Any) -> ComplianceStatus:
    """Return the compliance status for a vehicle speed and configured limit."""
    speed = _to_non_negative_decimal(vehicle_speed, "vehicle_speed")
    limit = _to_non_negative_decimal(speed_limit, "speed_limit")

    if speed < limit:
        return ComplianceStatus.SAFE
    if speed == limit:
        return ComplianceStatus.AT_LIMIT
    return ComplianceStatus.OVER_SPEED
