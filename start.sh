#!/bin/bash
# Start FastAPI in the background
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit in the foreground (Railway routes to this port)
uv run streamlit run streamlit_app.py \
  --server.port ${PORT:-8501} \
  --server.address 0.0.0.0 \
  --server.headless true