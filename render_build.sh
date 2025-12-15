#!/usr/bin/env bash
# Alternative build script name for Render auto-detection

set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Build C++ validator
cd cpp
make clean
make
chmod +x trajectory_validator
cd ..

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput


