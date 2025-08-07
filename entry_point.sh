#!/bin/sh

# Wait for DB to be ready (optional, in case DB starts slowly)
echo "Waiting for Postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Postgres started"

# Apply migrations
python manage.py migrate

# Ingest data from CSVs
python manage.py ingest_data

python manage.py runserver 0.0.0.0:8000
