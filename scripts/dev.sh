#!/usr/bin/env bash
# dev.sh — Start backend + (future) frontend
set -e

echo "Starting backend..."
cd backend
uv run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Open http://127.0.0.1:8000/api/health to verify."
echo "Press Ctrl+C to stop."

wait $BACKEND_PID
