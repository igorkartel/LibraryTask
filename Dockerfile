FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.4

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd \
    && pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* .

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

RUN sed -i 's/\r$//' /app/docker-entrypoint.sh \
    && chmod +x /app/docker-entrypoint.sh

EXPOSE 8004
