from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.api.main import app, get_narrator


@pytest.fixture
def mock_narrator():
    narrator = MagicMock()
    narrator.narrate.return_value = iter([b"audio-data"])
    return narrator


@pytest.fixture
def client(mock_narrator):
    app.dependency_overrides[get_narrator] = lambda: mock_narrator
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestHealth:
    def test_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestLanguages:
    def test_returns_supported_languages(self, client):
        response = client.get("/languages")
        assert response.status_code == 200
        data = response.json()
        assert "en" in data
        assert "de" in data
        assert "hi" in data

    def test_values_are_strings(self, client):
        response = client.get("/languages")
        for value in response.json().values():
            assert isinstance(value, str)


class TestNarrate:
    def test_streams_audio(self, client, mock_narrator):
        response = client.post("/narrate", json={"text": "Once upon a time", "language": "en"})
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"audio-data"

    def test_rejects_empty_text(self, client):
        response = client.post("/narrate", json={"text": "   ", "language": "en"})
        assert response.status_code == 422

    def test_rejects_unsupported_language(self, client):
        response = client.post("/narrate", json={"text": "Hello", "language": "xx"})
        assert response.status_code == 422

    def test_rejects_text_over_5000_chars(self, client):
        response = client.post("/narrate", json={"text": "x" * 5001, "language": "en"})
        assert response.status_code == 422

    def test_defaults_language_to_english(self, client, mock_narrator):
        client.post("/narrate", json={"text": "Hello"})
        mock_narrator.narrate.assert_called_once_with("Hello", "en")
