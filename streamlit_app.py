import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    API_BASE = st.secrets["API_BASE_URL"]
except Exception:
    API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Story Voice", page_icon="🎙️", layout="centered")

st.title("🎙️ Story Voice")
st.caption("Multilingual children's story narrator powered by ElevenLabs")


# --- Fetch languages and stories ---

@st.cache_data(ttl=3600)
def fetch_languages() -> dict[str, str]:
    try:
        r = httpx.get(f"{API_BASE}/languages", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"en": "English", "de": "German", "hi": "Hindi"}


@st.cache_data(ttl=60)
def fetch_stories(language_code: str) -> list[str]:
    try:
        r = httpx.get(f"{API_BASE}/stories/{language_code}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_audio(story_name: str, language_code: str) -> bytes | None:
    """Fetch and cache audio for a story+language pair for the app's lifetime."""
    try:
        r = httpx.post(
            f"{API_BASE}/narrate",
            json={"story_name": story_name, "language": language_code},
            timeout=60,
        )
        r.raise_for_status()
        return r.content
    except Exception:
        return None


languages = fetch_languages()

# --- UI ---

col1, col2 = st.columns([1, 2])

with col1:
    lang_labels = list(languages.values())
    lang_codes = list(languages.keys())
    selected_lang_label = st.selectbox("Language", lang_labels)
    selected_lang = lang_codes[lang_labels.index(selected_lang_label)]

stories = fetch_stories(selected_lang)

with col2:
    if not stories:
        st.warning(f"No stories found. Add `.txt` files to `data/stories/{selected_lang}/`.")
        st.stop()
    selected_story = st.selectbox("Choose a story", stories)

st.divider()

# Show cached audio immediately if available, without pressing the button
cache_key = (selected_story, selected_lang)
cached = st.session_state.get("audio_cache", {}).get(cache_key)

if cached:
    st.audio(cached, format="audio/mp3")
    st.download_button(
        label="⬇ Download MP3",
        data=cached,
        file_name=f"{selected_story}.mp3",
        mime="audio/mpeg",
    )
elif st.button("▶ Narrate", type="primary", use_container_width=True):
    with st.spinner(f'Narrating "{selected_story}"…'):
        audio_bytes = fetch_audio(selected_story, selected_lang)
        if audio_bytes:
            # Store in session state so switching stories and back doesn't re-fetch
            if "audio_cache" not in st.session_state:
                st.session_state["audio_cache"] = {}
            st.session_state["audio_cache"][cache_key] = audio_bytes
            st.rerun()
        else:
            st.error("Could not generate audio. Please try again.")

st.divider()
st.caption("Built to explore [ElevenLabs voice AI](http://elevenlabs.io/).")