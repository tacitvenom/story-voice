import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Story Voice", page_icon="🎙️", layout="centered")

st.title("🎙️ Story Voice")
st.caption("Multilingual children's story narrator powered by ElevenLabs")


# --- Fetch languages ---

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

if st.button("▶ Narrate", type="primary", use_container_width=True):
    with st.spinner(f'Narrating "{selected_story}"…'):
        try:
            response = httpx.post(
                f"{API_BASE}/narrate",
                json={"story_name": selected_story, "language": selected_lang},
                timeout=60,
            )
            response.raise_for_status()
            audio_bytes = response.content
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="⬇ Download MP3",
                data=audio_bytes,
                file_name=f"{selected_story}.mp3",
                mime="audio/mpeg",
            )
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = f"HTTP {e.response.status_code}"
            st.error(f"API error: {detail}")
        except Exception as e:
            st.error(f"Could not reach the API: {e}")

st.divider()
st.caption("Built to explore [ElevenLabs voice AI](http://elevenlabs.io/).")