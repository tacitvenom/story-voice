import os
from pathlib import Path

import click
from dotenv import load_dotenv

from app.core.narrator import StoryNarrator, SUPPORTED_LANGUAGES

load_dotenv()


@click.group()
def cli() -> None:
    """Story Voice — multilingual children's story narrator."""


@cli.command()
@click.argument("text")
@click.option(
    "--language", "-l",
    default="en",
    show_default=True,
    type=click.Choice(list(SUPPORTED_LANGUAGES)),
    help="Language for narration.",
)
@click.option(
    "--output", "-o",
    default="story.mp3",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Output MP3 file path.",
)
def narrate(text: str, language: str, output: Path) -> None:
    """Narrate TEXT as an MP3 file."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise click.ClickException("ELEVENLABS_API_KEY environment variable not set.")

    narrator = StoryNarrator(api_key=api_key)

    click.echo(f"Narrating in {SUPPORTED_LANGUAGES[language]['name']}...")
    saved = narrator.narrate_to_file(text, output, language)
    click.echo(f"✅ Saved to {saved}")


@cli.command()
def serve() -> None:
    """Start the Story Voice web server."""
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
