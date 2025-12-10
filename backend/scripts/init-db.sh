#!/bin/bash
set -e

echo "⏳ Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready"

echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Database initialized successfully!"