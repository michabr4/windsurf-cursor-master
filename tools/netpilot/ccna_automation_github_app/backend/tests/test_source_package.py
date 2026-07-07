import pytest

from app.services.source_package import get_source_package


def test_source_package_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOURCE_HTML_PATH", raising=False)
    result = get_source_package()
    assert "message" in result
    assert result["title"]
    assert result["metrics"] == []


def test_source_package_missing_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_HTML_PATH", "/tmp/does-not-exist-ccna-hub.html")
    result = get_source_package()
    assert "error" in result
    assert "not found" in result["error"].lower()
