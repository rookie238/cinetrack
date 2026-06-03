#!/usr/bin/env bash
# Render build script — her deploy'da çalışır
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_genres
python manage.py createsuperuser --noinput || true
