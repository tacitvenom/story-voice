# Story Voice 🎙️

A multilingual children's story narrator powered by [ElevenLabs](https://elevenlabs.io).

Pick a language among English, German and Hindi, pick a story from the available stories, and hear it read aloud in a warm, expressive voice.

**Live demo →** [Application link](https://story-voice.streamlit.app/)
- [Railway](railway.com) for the backend service
- [Streamlit Community](https://streamlit.io/cloud) for the frontend service

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

## Quickstart locally

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

## Quickstart with Docker
```bash
docker build -t story-voice:latest .
docker run -p 8000:8000 -p 8501:8501 --env-file .env story-voice:latest
```

## Stories Sources
- [English](https://www.writerswrite.com/journal/childrens-stories/)
- [German](https://gute-nacht-geschichten.com/kindergeschichten/)
- [Hindi](https://librarykvrishikesh.wordpress.com/%e0%a4%aa%e0%a4%82%e0%a4%9a%e0%a4%a4%e0%a4%82%e0%a4%a4%e0%a5%8d%e0%a4%b0-%e0%a4%95%e0%a5%80-%e0%a4%b8%e0%a4%ae%e0%a5%8d%e0%a4%aa%e0%a5%82%e0%a4%b0%e0%a5%8d%e0%a4%a3-%e0%a4%95%e0%a4%b9%e0%a4%be/)

## What I'd build next

- **Voice selection**: let users audition different ElevenLabs voices before narrating
- **Story generation**: integrate an LLM to co-write stories before narrating them
- **SSML support**: add expressive pauses and emphasis for dramatic moments
- **More languages**: ElevenLabs supports 70+ — easy to extend `SUPPORTED_LANGUAGES`

---

*Built as a technical exploration of ElevenLabs' voice AI APIs.*
