# Story Voice 🎙️

A multilingual children's story narrator powered by [ElevenLabs](https://elevenlabs.io).

Pick a language among English, German and Hindi, pick a story from the available stories, and hear it read aloud in a warm, expressive voice.

**Live demo →** *(TODO: deploy link here)*

---

## The problem

Parents, teachers, and content creators need engaging multilingual audio for children's stories. Recording high-quality narrations manually is expensive and slow; machine TTS has historically sounded robotic. ElevenLabs changes that.

## What it does

- Text → expressive MP3 narration via ElevenLabs Turbo v2.5
- Three languages: English 🇬🇧, German 🇩🇪, Hindi 🇮🇳
- Streaming audio playback in-browser, with the option to download the MP3
- CLI for batch narration workflows

## Stack

- **Backend**: FastAPI + ElevenLabs Python SDK
- **Frontend**: Streamlit
- **Package management**: `uv`
- **Testing**: `pytest` with mocked ElevenLabs client

## Quickstart

```bash
# 1. Install dependencies
uv sync

# 2. Set your API key
cp .env.example .env
# edit .env and add your ELEVENLABS_API_KEY

# 3. Run the server
./start.sh
# → open http://localhost:8501
```


## Run tests

```bash
uv run py.test --cov=app tests/
```

## Stories Sources
- [English](https://www.writerswrite.com/journal/childrens-stories/)
- [German]()
- [Hindi]()

## What I'd build next

- **Voice selection**: let users audition different ElevenLabs voices before narrating
- **Story generation**: integrate an LLM to co-write stories before narrating them
- **SSML support**: add expressive pauses and emphasis for dramatic moments
- **More languages**: ElevenLabs supports 70+ — easy to extend `SUPPORTED_LANGUAGES`
- **Deployment**: Hugging Face Spaces or Fly.io for a shareable public demo

---

*Built as a technical exploration of ElevenLabs' voice AI APIs.*
