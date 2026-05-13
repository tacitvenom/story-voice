from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

from app.core.narrator import StoryNarrator, SUPPORTED_LANGUAGES


@pytest.fixture
def mock_client():
    with patch("app.core.narrator.ElevenLabs") as MockElevenLabs:
        mock_instance = MagicMock()
        MockElevenLabs.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def narrator(mock_client):
    return StoryNarrator(api_key="test-key")


class TestSupportedLanguages:
    def test_returns_all_languages(self, narrator):
        langs = narrator.supported_languages()
        assert set(langs.keys()) == {"en", "de", "hi"}

    def test_values_are_display_names(self, narrator):
        langs = narrator.supported_languages()
        assert langs["en"] == "English"
        assert langs["de"] == "German"
        assert langs["hi"] == "Hindi"


class TestNarrate:
    def test_returns_audio_stream(self, narrator, mock_client):
        mock_client.text_to_speech.convert.return_value = iter([b"audio-chunk"])
        result = list(narrator.narrate("Once upon a time...", "en"))
        assert result == [b"audio-chunk"]

    def test_raises_on_empty_text(self, narrator):
        with pytest.raises(ValueError, match="empty"):
            list(narrator.narrate("   ", "en"))

    def test_raises_on_unsupported_language(self, narrator):
        with pytest.raises(ValueError, match="Unsupported language"):
            list(narrator.narrate("Hello", "zz"))

    def test_defaults_to_english(self, narrator, mock_client):
        mock_client.text_to_speech.convert.return_value = iter([b"chunk"])
        narrator.narrate("Hello")
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["voice_id"] == SUPPORTED_LANGUAGES["en"]["voice_id"]

    def test_uses_correct_voice_for_language(self, narrator, mock_client):
        mock_client.text_to_speech.convert.return_value = iter([b"chunk"])
        narrator.narrate("Hallo Welt", "de")
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["voice_id"] == SUPPORTED_LANGUAGES["de"]["voice_id"]


class TestNarrateToFile:
    def test_writes_audio_to_file(self, narrator, mock_client, tmp_path):
        mock_client.text_to_speech.convert.return_value = iter([b"chunk1", b"chunk2"])
        output = tmp_path / "story.mp3"
        result = narrator.narrate_to_file("Once upon a time", output, "en")
        assert result == output
        assert output.read_bytes() == b"chunk1chunk2"

    def test_creates_parent_directories(self, narrator, mock_client, tmp_path):
        mock_client.text_to_speech.convert.return_value = iter([b"data"])
        output = tmp_path / "nested" / "dir" / "story.mp3"
        narrator.narrate_to_file("A story", output, "en")
        assert output.exists()

    def test_returns_path_object(self, narrator, mock_client, tmp_path):
        mock_client.text_to_speech.convert.return_value = iter([b"data"])
        result = narrator.narrate_to_file("A story", tmp_path / "out.mp3", "en")
        assert isinstance(result, Path)
