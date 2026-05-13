#!/usr/bin/env bash
# ============================================================
# Render start script.
# Render's free tier filesystem is wiped on every cold boot,
# so we rebuild the ChromaDB vector store before serving traffic.
# ============================================================
set -e

echo "==> Rebuilding vector DB from data/..."
python ingest.py

echo "==> Starting FastAPI server on port $PORT..."
exec uvicorn api:app --host 0.0.0.0 --port "$PORT"
