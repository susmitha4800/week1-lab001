import pytest
from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before each test."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_expected_keys():
    """Verify the /activities endpoint returns the seeded activity list."""
    client = TestClient(app)
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_adds_participant():
    """Ensure signing up adds a participant to the activity's participant list."""

    client = TestClient(app)
    email = "testuser@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"].startswith("Signed up")

    # Verify participant was added
    activities_data = client.get("/activities").json()
    assert email in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_returns_bad_request():
    """Ensure signing up someone already registered returns a 400 error."""
    client = TestClient(app)
    email = "michael@mergington.edu"  # already signed up in seed data

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_remove_participant():
    """Verify that deleting a participant actually removes them from the activity."""

    client = TestClient(app)
    email = "daniel@mergington.edu"

    response = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert response.status_code == 200
    assert response.json()["message"].startswith("Removed")

    activities_data = client.get("/activities").json()
    assert email not in activities_data["Chess Club"]["participants"]
