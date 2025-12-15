#!/usr/bin/env bash
# Build script for Render.com deployment

set -o errexit  # Exit on error

echo "📁 Creating media directories..."
mkdir -p /opt/render/project/src/media/corridors
mkdir -p /opt/render/project/src/media/trajectories
chmod -R 755 /opt/render/project/src/media
echo "✓ Media directories created"

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

