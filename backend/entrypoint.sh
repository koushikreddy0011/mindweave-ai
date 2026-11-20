#!/bin/sh
set -e
echo "[MindWeave Entrypoint] Running database migrations..."
alembic upgrade head
echo "[MindWeave Entrypoint] Starting Uvicorn production server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
