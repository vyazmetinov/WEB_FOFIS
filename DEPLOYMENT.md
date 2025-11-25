# FOFIS Deployment Guide

## Quick Start (Development)

### 1. Automated Setup (Recommended)

```bash
cd /Users/ivan/PycharmProjects/FOFIS
chmod +x setup.sh
./setup.sh
```

This script will:
- Check Python and g++ installation
- Create virtual environment
- Install all dependencies
- Compile C++ validator
- Create necessary directories
- Initialize database

### 2. Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Compile C++ module
cd cpp
make
cd ..

# Setup database
python manage.py makemigrations
python manage.py migrate

# Create media directories
mkdir -p media/corridors media/trajectories static
```

### 3. Run Development Server

```bash
source venv/bin/activate
python manage.py runserver
```

Access at: **http://127.0.0.1:8000/**

## Testing the Application

### 1. Upload Sample Data

Navigate to http://127.0.0.1:8000/

In the file upload table:
1. Upload `sample_data/corridor.txt` as corridor file
2. Upload `sample_data/trajectory.txt` as trajectory file
3. Wait for processing (should be automatic)

### 2. View Results

- Green corridor line should appear on map
- Table row should show metrics (mean deviation, mean speed)
- Click the row to load data for playback

### 3. Test Playback

1. Click **▶ Play** button
2. Watch the blue aircraft marker move
3. Try different speeds (1×, 2×, 4×, 8×, 16×)
4. Use the time slider to jump around
5. Click **⏸ Pause** to pause

### 4. Test Violations

Upload the violation scenario:
- `sample_data/corridor_violation.txt`
- `sample_data/trajectory_violation.txt`

This will show higher deviation values.

### 5. Run Unit Tests

```bash
python manage.py test
```

Expected output: All tests should pass.

## Creating Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create username and password.

Access admin at: **http://127.0.0.1:8000/admin/**

## Production Deployment

### Prerequisites

- Ubuntu/Debian server
- Python 3.8+
- PostgreSQL
- Nginx
- Domain name (optional)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y g++ make
```

### 2. PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE fofis_db;
CREATE USER fofis_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fofis_db TO fofis_user;
\q
```

### 3. Application Setup

```bash
# Create app directory
sudo mkdir -p /var/www/fofis
sudo chown $USER:$USER /var/www/fofis
cd /var/www/fofis

# Clone/copy application files
# (Assume files are already on server)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Compile C++ validator
cd cpp
make
cd ..
```

### 4. Django Configuration

Create `.env` file:

```bash
SECRET_KEY=your_very_long_random_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,server_ip
DATABASE_URL=postgresql://fofis_user:your_secure_password@localhost/fofis_db
```

Update `fofis_project/settings.py`:

```python
import os
from pathlib import Path

# Load environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# PostgreSQL database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fofis_db',
        'USER': 'fofis_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = '/var/www/fofis/staticfiles/'
MEDIA_ROOT = '/var/www/fofis/media/'
```

### 5. Database Migration

```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 6. Gunicorn Setup

Create systemd service file: `/etc/systemd/system/fofis.service`

```ini
[Unit]
Description=FOFIS Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/fofis
Environment="PATH=/var/www/fofis/venv/bin"
ExecStart=/var/www/fofis/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/fofis/fofis.sock \
    fofis_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start Gunicorn:

```bash
sudo systemctl start fofis
sudo systemctl enable fofis
sudo systemctl status fofis
```

### 7. Nginx Configuration

Create: `/etc/nginx/sites-available/fofis`

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        alias /var/www/fofis/staticfiles/;
    }

    location /media/ {
        alias /var/www/fofis/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/fofis/fofis.sock;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/fofis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 9. Firewall Configuration

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 10. Verify Deployment

Visit: **https://yourdomain.com/**

Check:
- Site loads correctly
- Can upload files
- Map displays
- Playback works

## Monitoring & Maintenance

### Check Application Logs

```bash
# Gunicorn logs
sudo journalctl -u fofis

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs (if configured)
tail -f /var/www/fofis/logs/django.log
```

### Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart fofis

# Restart Nginx
sudo systemctl restart nginx

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Database Backup

```bash
# Backup
sudo -u postgres pg_dump fofis_db > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql fofis_db < backup_20231115.sql
```

### Update Application

```bash
cd /var/www/fofis
source venv/bin/activate

# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Recompile C++ if changed
cd cpp && make && cd ..

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl restart fofis
```

## Performance Tuning

### 1. Gunicorn Workers

Rule of thumb: `workers = (2 × num_cores) + 1`

```bash
# For 2 CPU cores
workers = 5
```

### 2. Database Connection Pooling

Install: `pip install django-db-connection-pool`

Configure in settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 10,
        }
    }
}
```

### 3. Redis Caching

Install: `pip install django-redis`

Configure:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 4. Celery for Async Processing

Install: `pip install celery redis`

Create `celery.py`:

```python
from celery import Celery

app = Celery('fofis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Process files asynchronously in background.

## Security Hardening

### 1. Environment Variables

Use `.env` file (never commit to git):

```bash
pip install python-decouple
```

In settings.py:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 2. HTTPS Only

In settings.py:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Security Headers

```python
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### 4. File Upload Limits

In settings.py:

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

### 5. CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

## Troubleshooting Production Issues

### Issue: 502 Bad Gateway

**Cause**: Gunicorn not running

**Fix**:
```bash
sudo systemctl status fofis
sudo systemctl restart fofis
```

### Issue: Static files not loading

**Cause**: STATIC_ROOT not configured

**Fix**:
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: Database connection errors

**Cause**: PostgreSQL not running or wrong credentials

**Fix**:
```bash
sudo systemctl status postgresql
sudo systemctl restart postgresql
# Check settings.py database configuration
```

### Issue: Permission denied on file uploads

**Cause**: Wrong permissions on media directory

**Fix**:
```bash
sudo chown -R www-data:www-data /var/www/fofis/media
sudo chmod -R 755 /var/www/fofis/media
```

### Issue: C++ validator not found

**Cause**: Path not correct or not compiled

**Fix**:
```bash
cd /var/www/fofis/cpp
make
chmod +x trajectory_validator
# Check CPP_VALIDATOR_PATH in settings.py
```

## Backup Strategy

### What to Backup

1. **Database**: PostgreSQL dumps
2. **Media files**: User uploads
3. **Configuration**: .env, settings
4. **Code**: Git repository

### Automated Backup Script

Create `/var/www/fofis/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/fofis"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
sudo -u postgres pg_dump fofis_db > "$BACKUP_DIR/db_$DATE.sql"

# Media files backup
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /var/www/fofis/media/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

Add to cron:

```bash
sudo crontab -e
# Add line:
0 2 * * * /var/www/fofis/backup.sh
```

## Monitoring

### Health Check Endpoint

Add to `monitoring/views.py`:

```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok'})
```

### Monitoring Tools

- **Uptime monitoring**: UptimeRobot, Pingdom
- **Error tracking**: Sentry
- **Performance**: New Relic, DataDog
- **Server monitoring**: Prometheus + Grafana

## Support & Resources

- Django Documentation: https://docs.djangoproject.com/
- Gunicorn Documentation: https://gunicorn.org/
- Nginx Documentation: https://nginx.org/en/docs/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

---

**FOFIS Deployment** - From development to production.

