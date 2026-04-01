#!/usr/bin/env bash
set -e

cd /app

python -m alembic upgrade head
exec uvicorn src.main.web:app --host 0.0.0.0 --port "${PORT:-10000}"
