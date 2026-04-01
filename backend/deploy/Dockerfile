FROM python:3.11-slim AS backend

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

COPY pyproject.toml poetry.lock* alembic.ini /app/

COPY deploy/configs /app/deploy/configs

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY src /app/src

CMD ["uvicorn", "src.main.web:app", "--host", "0.0.0.0", "--port", "10000"]
