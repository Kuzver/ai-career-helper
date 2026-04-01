#!/usr/bin/env bash
set -e

cd /app

echo "Running migrations..."
python -m alembic upgrade head

echo "Running seed..."
python -m src.infra.postgres.seed

echo "Starting server..."
exec uvicorn src.main.web:app --host 0.0.0.0 --port "${PORT:-10000}"
