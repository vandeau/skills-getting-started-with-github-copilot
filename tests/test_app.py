from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants for each activity, restore after test
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    for k, v in original.items():
        activities[k]["participants"] = v[:]


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Ensure known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister():
    client = TestClient(app)
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"

    # Verify participant added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"

    # Verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
