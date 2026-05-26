from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_plan() -> None:
    response = client.post(
        "/api/plan",
        json={"exam_date": "2026-09-01", "hours_per_week": 8, "current_level": "beginner"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "weekly_plan" in body
    assert len(body["weekly_plan"]) == 4


def test_flashcards_from_database() -> None:
    response = client.get("/api/flashcards")
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) >= 3
    assert all("question" in card and "domain" in card for card in cards)


def test_practice_questions() -> None:
    response = client.get("/api/practice-questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) >= 5


def test_weak_areas() -> None:
    response = client.post(
        "/api/weak-areas",
        json=[{"domain": "REST APIs", "score_percent": 55, "attempts": 2}],
    )
    assert response.status_code == 200
    areas = response.json()
    assert len(areas) >= 1
    assert areas[0]["domain"] == "REST APIs"


def test_domains_list() -> None:
    response = client.get("/api/domains")
    assert response.status_code == 200
    domains = response.json()["domains"]
    assert "REST APIs" in domains
