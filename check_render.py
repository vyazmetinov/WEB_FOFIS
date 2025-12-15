#!/usr/bin/env python3
"""
Script to check Render.com deployment settings
Run this in Render Shell to diagnose issues
"""
import os
import sys
from pathlib import Path

print("=" * 60)
print("FOFIS Render.com Diagnostic Check")
print("=" * 60)
print()

# Check Python version
print("✓ Python version:", sys.version)
print()

# Check Django
try:
    import django
    print("✓ Django version:", django.VERSION)
except ImportError:
    print("✗ Django not installed!")
print()

# Check environment variables
print("Environment Variables:")
print("-" * 60)
env_vars = {
    'MEDIA_ROOT': os.environ.get('MEDIA_ROOT'),
    'DATABASE_URL': os.environ.get('DATABASE_URL', 'NOT SET'),
    'SECRET_KEY': '***' if os.environ.get('SECRET_KEY') else 'NOT SET',
    'DEBUG': os.environ.get('DEBUG'),
    'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE'),
    'RENDER_EXTERNAL_HOSTNAME': os.environ.get('RENDER_EXTERNAL_HOSTNAME'),
}

for key, value in env_vars.items():
    status = "✓" if value and value != 'NOT SET' else "✗"
    print(f"{status} {key}: {value}")
print()

# Check media directories
print("Media Directories:")
print("-" * 60)
media_root = os.environ.get('MEDIA_ROOT', '/opt/render/project/src/media')
paths_to_check = [
    media_root,
    f"{media_root}/corridors",
    f"{media_root}/trajectories",
]

for path in paths_to_check:
    p = Path(path)
    exists = p.exists()
    is_dir = p.is_dir() if exists else False
    writable = os.access(path, os.W_OK) if exists else False
    
    status = "✓" if exists and is_dir and writable else "✗"
    info = []
    if not exists:
        info.append("NOT EXISTS")
    if exists and not is_dir:
        info.append("NOT DIR")
    if exists and not writable:
        info.append("NOT WRITABLE")
    
    info_str = f" ({', '.join(info)})" if info else " (OK)"
    print(f"{status} {path}{info_str}")
print()

# Check C++ validator
print("C++ Validator:")
print("-" * 60)
cpp_path = Path("/opt/render/project/src/cpp/trajectory_validator")
if cpp_path.exists():
    executable = os.access(cpp_path, os.X_OK)
    status = "✓" if executable else "✗"
    print(f"{status} {cpp_path} {'(executable)' if executable else '(NOT executable)'}")
else:
    print(f"✗ {cpp_path} (NOT EXISTS)")
print()

# Check database connection
print("Database Connection:")
print("-" * 60)
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fofis_project.settings')
    import django
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection OK")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
print()

# Check installed packages
print("Key Packages:")
print("-" * 60)
packages = [
    'django',
    'djangorestframework',
    'psycopg2',
    'gunicorn',
    'whitenoise',
    'corsheaders',
]

for package in packages:
    try:
        mod = __import__(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {package}: {version}")
    except ImportError:
        print(f"✗ {package}: NOT INSTALLED")
print()

print("=" * 60)
print("Diagnostic check complete!")
print("=" * 60)

