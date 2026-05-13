from pathlib import Path
from unittest.mock import patch
import pytest

from app.core.story_loader import list_stories, load_story


@pytest.fixture
def stories_dir(tmp_path):
    """Create a tmp stories dir with language subdirs and sample files."""
    for lang, files in {
        "en": {"the_fox.txt": "Once upon a time there was a fox."},
        "de": {"brave_knight.txt": "Ein Ritter ritt ins Tal."},
        "hi": {"sun_and_moon.txt": "सूरज और चाँद की कहानी।"},
    }.items():
        lang_dir = tmp_path / lang
        lang_dir.mkdir()
        for fname, content in files.items():
            (lang_dir / fname).write_text(content, encoding="utf-8")
    return tmp_path


class TestListStories:
    def test_returns_display_names_for_language(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            result = list_stories("en")
        assert "The Fox" in result

    def test_returns_stories_for_each_language(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            assert "Brave Knight" in list_stories("de")
            assert "Sun And Moon" in list_stories("hi")

    def test_values_are_paths(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            result = list_stories("en")
        assert all(isinstance(v, Path) for v in result.values())

    def test_returns_empty_when_lang_dir_missing(self, tmp_path):
        with patch("app.core.story_loader.STORIES_DIR", tmp_path):
            result = list_stories("en")
        assert result == {}

    def test_raises_on_unsupported_language(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            with pytest.raises(ValueError, match="Unsupported language"):
                list_stories("zz")

    def test_ignores_non_txt_files(self, stories_dir):
        (stories_dir / "en" / "notes.md").write_text("not a story")
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            result = list_stories("en")
        assert "Notes" not in result

    def test_sorted_alphabetically(self, stories_dir):
        (stories_dir / "en" / "another_tale.txt").write_text("Another tale.")
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            keys = list(list_stories("en").keys())
        assert keys == sorted(keys)


class TestLoadStory:
    def test_returns_story_text(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            text = load_story("The Fox", "en")
        assert "fox" in text.lower()

    def test_loads_correct_language(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            text = load_story("Brave Knight", "de")
        assert "Ritter" in text

    def test_raises_for_unknown_story(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            with pytest.raises(ValueError, match="not found"):
                load_story("Nonexistent Story", "en")

    def test_raises_for_story_in_wrong_language(self, stories_dir):
        with patch("app.core.story_loader.STORIES_DIR", stories_dir):
            with pytest.raises(ValueError, match="not found"):
                load_story("The Fox", "de")