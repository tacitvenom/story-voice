from pathlib import Path
from typing import Iterator

from elevenlabs import ElevenLabs
from elevenlabs.types import VoiceSettings

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
    "de": {"name": "German", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
    "hi": {"name": "Hindi", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
}

DEFAULT_VOICE_SETTINGS = VoiceSettings(
    stability=0.75,
    similarity_boost=0.85,
    style=0.35,        # slight expressiveness for storytelling
    use_speaker_boost=True,
)


class StoryNarrator:
    """Converts story text to audio using ElevenLabs TTS."""

    def __init__(self, api_key: str) -> None:
        self._client = ElevenLabs(api_key=api_key)

    def supported_languages(self) -> dict[str, str]:
        """Return mapping of language code -> display name."""
        return {code: meta["name"] for code, meta in SUPPORTED_LANGUAGES.items()}

    def narrate(self, text: str, language_code: str = "en") -> Iterator[bytes]:
        """Stream audio bytes for the given story text and language."""
        if not text.strip():
            raise ValueError("Story text must not be empty.")
        if language_code not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language_code}'. "
                f"Choose from: {list(SUPPORTED_LANGUAGES)}"
            )

        voice_id = SUPPORTED_LANGUAGES[language_code]["voice_id"]

        return self._client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5",
            voice_settings=DEFAULT_VOICE_SETTINGS,
            output_format="mp3_44100_128",
        )

    def narrate_to_file(
        self, text: str, output_path: Path, language_code: str = "en"
    ) -> Path:
        """Narrate story and save to an MP3 file. Returns the output path."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        audio_stream = self.narrate(text, language_code)
        with output_path.open("wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return output_path
