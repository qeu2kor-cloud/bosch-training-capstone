import pytest

from vehicle_speed_checker.api import create_app


@pytest.fixture()
def client():
    return create_app().test_client()


def test_check_endpoint_returns_status(client):
    response = client.post("/check", json={"vehicle_speed": 79, "speed_limit": 80})

    assert response.status_code == 200
    assert response.get_json() == {"status": "SAFE"}


@pytest.mark.parametrize(
    ("vehicle_speed", "expected_error"),
    [
        (-1, "vehicle_speed must be a non-negative number"),
        (None, "vehicle_speed must be a non-negative number"),
        ("abc", "vehicle_speed must be a non-negative number"),
    ],
)
def test_check_endpoint_returns_validation_error(client, vehicle_speed, expected_error):
    response = client.post(
        "/check",
        json={"vehicle_speed": vehicle_speed, "speed_limit": 80},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": expected_error}


@pytest.mark.parametrize("body", [None, [], {"vehicle_speed": 80}])
def test_check_endpoint_rejects_malformed_or_incomplete_body(client, body):
    response = client.post("/check", json=body)

    assert response.status_code == 400
    assert "error" in response.get_json()
