#!/bin/bash

echo "Waiting for database to be ready..."
while ! nc -z library-db 5432; do
  sleep 0.1
done
echo "Database is up."

echo "Applying database migrations..."
python -m alembic upgrade head

echo "Starting Uvicorn server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
