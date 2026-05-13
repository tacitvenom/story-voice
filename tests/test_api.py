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


class TestStoriesList:
    def test_returns_stories_for_language(self, client):
        with patch("app.api.main.list_stories", return_value={"The Fox": "data/stories/en/the_fox.txt"}):
            response = client.get("/stories/en")
        assert response.status_code == 200
        assert "The Fox" in response.json()

    def test_returns_empty_when_no_stories(self, client):
        with patch("app.api.main.list_stories", return_value={}):
            response = client.get("/stories/en")
        assert response.json() == []

    def test_returns_422_for_unsupported_language(self, client):
        with patch("app.api.main.list_stories", side_effect=ValueError("Unsupported language")):
            response = client.get("/stories/zz")
        assert response.status_code == 422


class TestNarrate:
    def test_streams_audio(self, client, mock_narrator):
        with patch("app.api.main.load_story", return_value="Once upon a time"):
            response = client.post("/narrate", json={"story_name": "The Fox", "language": "en"})
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"audio-data"

    def test_rejects_empty_story_name(self, client):
        response = client.post("/narrate", json={"story_name": "  ", "language": "en"})
        assert response.status_code == 422

    def test_rejects_unsupported_language(self, client):
        response = client.post("/narrate", json={"story_name": "The Fox", "language": "xx"})
        assert response.status_code == 422

    def test_returns_422_when_story_not_found(self, client, mock_narrator):
        with patch("app.api.main.load_story", side_effect=ValueError("Story not found")):
            response = client.post("/narrate", json={"story_name": "Missing", "language": "en"})
        assert response.status_code == 422

    def test_defaults_language_to_english(self, client, mock_narrator):
        with patch("app.api.main.load_story", return_value="Hello"):
            client.post("/narrate", json={"story_name": "The Fox"})
        mock_narrator.narrate.assert_called_once_with("Hello", "en")

    def test_load_story_called_with_language(self, client, mock_narrator):
        with patch("app.api.main.load_story", return_value="Hallo") as mock_load:
            client.post("/narrate", json={"story_name": "Brave Knight", "language": "de"})
        mock_load.assert_called_once_with("Brave Knight", "de")