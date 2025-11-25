#!/usr/bin/env bash
# Build script for Render.com deployment

set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Building C++ trajectory validator..."
cd cpp
make clean
make
chmod +x trajectory_validator
cd ..

echo "📊 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"

