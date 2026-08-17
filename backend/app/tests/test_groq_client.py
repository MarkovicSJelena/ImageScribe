import pytest

from app.core.config import settings
from app.services.groq_client import get_client


def test_get_client_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        get_client()


def test_get_client_is_cached_when_key_present(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-key")
    first = get_client()
    second = get_client()
    assert first is second
