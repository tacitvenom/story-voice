import os
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from app.core.narrator import StoryNarrator, SUPPORTED_LANGUAGES

load_dotenv()

app = FastAPI(
    title="Story Voice",
    description="Multilingual children's story narrator powered by ElevenLabs",
    version="0.1.0",
)


# --- Dependency ---

def get_narrator() -> StoryNarrator:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not configured.")
    return StoryNarrator(api_key=api_key)


# --- Schemas ---

class NarrateRequest(BaseModel):
    text: str
    language: str = "en"

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Story text must not be empty.")
        if len(v) > 5000:
            raise ValueError("Story text must be 5000 characters or fewer.")
        return v.strip()

    @field_validator("language")
    @classmethod
    def language_supported(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {list(SUPPORTED_LANGUAGES)}")
        return v


# --- Routes ---

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/languages")
def list_languages() -> dict:
    return {
        code: meta["name"]
        for code, meta in SUPPORTED_LANGUAGES.items()
    }


@app.post("/narrate")
def narrate(
    request: NarrateRequest,
    narrator: Annotated[StoryNarrator, Depends(get_narrator)],
) -> StreamingResponse:
    """Stream MP3 audio of the narrated story."""
    try:
        audio_stream = narrator.narrate(request.text, request.language)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=story.mp3"},
    )


# Serve frontend (must come after API routes)
_static_dir = Path(__file__).parent.parent / "static"
app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
