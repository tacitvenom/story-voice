from pathlib import Path

from app.core.narrator import SUPPORTED_LANGUAGES

STORIES_DIR = Path(__file__).parents[2] / "data" / "stories"


def list_stories(language_code: str) -> dict[str, Path]:
    """Return mapping of display name -> file path for all .txt stories in a language dir."""
    if language_code not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language_code}'. "
            f"Choose from: {list(SUPPORTED_LANGUAGES)}"
        )
    lang_dir = STORIES_DIR / language_code
    if not lang_dir.exists():
        return {}
    return {
        p.stem.replace("_", " ").title(): p
        for p in sorted(lang_dir.glob("*.txt"))
    }


def load_story(name: str, language_code: str) -> str:
    """Load story text by display name and language. Raises ValueError if not found."""
    stories = list_stories(language_code)
    if name not in stories:
        raise ValueError(f"Story '{name}' not found for language '{language_code}'. Available: {list(stories)}")
    return stories[name].read_text(encoding="utf-8")