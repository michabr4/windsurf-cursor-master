import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _sign(payload: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_github_webhook_rejects_without_secret(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "")
    payload = json.dumps({"action": "created"}).encode()
    response = client.post(
        "/webhooks/github",
        content=payload,
        headers={
            "X-GitHub-Event": "installation",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )
    assert response.status_code == 401


def test_github_webhook_accepts_valid_signature(monkeypatch) -> None:
    secret = "test-webhook-secret"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secret)

    body = {
        "action": "created",
        "installation": {
            "id": 12345,
            "account": {"login": "demo-org", "type": "Organization"},
        },
    }
    payload = json.dumps(body).encode()
    response = client.post(
        "/webhooks/github",
        content=payload,
        headers={
            "X-GitHub-Event": "installation",
            "X-Hub-Signature-256": _sign(payload, secret),
            "X-GitHub-Delivery": "test-delivery-1",
        },
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    events = client.get("/api/github/events").json()["events"]
    assert len(events) >= 1
