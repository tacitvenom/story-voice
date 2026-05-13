FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
RUN uv sync --no-dev

COPY app/ app/
COPY data/ data/
COPY streamlit_app.py .
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000 8501
CMD ["./start.sh"]
