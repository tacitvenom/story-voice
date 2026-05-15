import os
from typing import Annotated
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from elevenlabs.core import ApiError

from app.core.narrator import StoryNarrator, SUPPORTED_LANGUAGES
from app.core.story_loader import list_stories, load_story


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
    story_name: str
    language: str = "en"

    @field_validator("story_name")
    @classmethod
    def story_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Story name must not be empty.")
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
def language_list() -> dict:
    return {
        code: meta["name"]
        for code, meta in SUPPORTED_LANGUAGES.items()
    }


@app.get("/stories/{language_code}")
def stories_list(language_code: str) -> list[str]:
    """List available stories for a given language code (e.g. /stories/en)."""
    try:
        return list(list_stories(language_code).keys())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/narrate")
def narrate(
    request: NarrateRequest,
    narrator: Annotated[StoryNarrator, Depends(get_narrator)],
) -> StreamingResponse:
    """Load story by name and language, then stream MP3 audio."""
    try:
        text = load_story(request.story_name, request.language)
        audio_bytes = b"".join(narrator.narrate(text, request.language))  # network call happens here
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ApiError as e:
        if e.status_code == 401 and isinstance(e.body, dict):
            status = e.body.get("detail", {}).get("status", "")
            message = e.body.get("detail", {}).get("message", "ElevenLabs error.")
            if status == "quota_exceeded":
                raise HTTPException(status_code=402, detail=message)
        raise HTTPException(status_code=502, detail="ElevenLabs API error.")
 
    # RFC 5987: percent-encode filename to support non-ASCII scripts (e.g. Devanagari)
    safe_filename = quote(f"{request.story_name}.mp3", safe="")
    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{safe_filename}"},
    )