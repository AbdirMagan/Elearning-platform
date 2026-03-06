# 🚀 Deployment Guide

This guide will help you deploy your e-learning platform to production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [Database Configuration](#database-configuration)
- [Environment Configuration](#environment-configuration)
- [Static & Media Files](#static--media-files)
- [Gunicorn Setup](#gunicorn-setup)
- [Nginx Configuration](#nginx-configuration)
- [SSL Certificate](#ssl-certificate)
- [WaafiPay Production Setup](#waafipay-production-setup)

## Prerequisites

- Ubuntu 20.04+ server
- Root or sudo access
- Domain name (optional but recommended)
- WaafiPay merchant account

## Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
sudo apt install python3-pip python3-dev python3-venv \
    postgresql postgresql-contrib nginx curl \
    libpq-dev git -y
```

### 3. Clone Repository
```bash
cd /var/www
sudo git clone <your-repo-url> elearning
cd elearning
sudo chown -R $USER:$USER /var/www/elearning
```

## Database Configuration

### 1. Create PostgreSQL Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE elearning_db;
CREATE USER elearning_user WITH PASSWORD 'your_strong_password';
ALTER ROLE elearning_user SET client_encoding TO 'utf8';
ALTER ROLE elearning_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE elearning_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE elearning_db TO elearning_user;
\q
```

### 2. Update .env
```bash
DATABASE_URL=postgresql://elearning_user:your_strong_password@localhost:5432/elearning_db
```

## Environment Configuration

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configure Environment Variables
```bash
nano .env
```

Update the following:
```
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip

DATABASE_URL=postgresql://elearning_user:password@localhost:5432/elearning_db

# WaafiPay Production
WAAFIPAY_MERCHANT_ID=your_production_merchant_id
WAAFIPAY_API_USER_ID=your_production_api_user_id
WAAFIPAY_API_KEY=your_production_api_key
WAAFIPAY_MODE=production
WAAFIPAY_CALLBACK_URL=https://your-domain.com/payments/callback/

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## Static & Media Files

### 1. Create Directories
```bash
sudo mkdir -p /var/www/elearning/staticfiles
sudo mkdir -p /var/www/elearning/media
sudo chown -R www-data:www-data /var/www/elearning/media
sudo chmod -R 755 /var/www/elearning/media
```

### 2. For S3 (Recommended for Production)
Install boto3:
```bash
pip install boto3 django-storages
```

Update settings.py:
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'storages',
]

# S3 Configuration
if not DEBUG:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## Gunicorn Setup

### 1. Create Gunicorn Socket
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### 2. Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/elearning
Environment="PATH=/var/www/elearning/venv/bin"
ExecStart=/var/www/elearning/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          elearning.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Start Gunicorn
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
```

## Nginx Configuration

### 1. Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/elearning
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/elearning/staticfiles/;
    }

    location /media/ {
        alias /var/www/elearning/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/elearning /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Configure Firewall
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## SSL Certificate

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Auto-renewal
Certbot automatically sets up renewal. Test with:
```bash
sudo certbot renew --dry-run
```

## WaafiPay Production Setup

### 1. Get Production Credentials
- Log in to [WaafiPay Dashboard](https://dashboard.waafipay.com)
- Navigate to API Settings
- Copy production credentials
- Update callback URL to production domain

### 2. Test Payment Flow
1. Create a test course
2. Attempt to purchase
3. Complete payment with WaafiPay
4. Verify enrollment
5. Check transaction in admin panel

### 3. Monitor Transactions
- Set up logging for payments
- Monitor callback endpoint
- Check WaafiPay dashboard regularly

## Maintenance

### Update Application
```bash
cd /var/www/elearning
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### View Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Application logs
tail -f /var/www/elearning/logs/django.log
```

### Database Backup
```bash
# Backup
pg_dump elearning_db > backup_$(date +%Y%m%d).sql

# Restore
psql elearning_db < backup_20240101.sql
```

## Monitoring & Performance

### Install monitoring tools
```bash
pip install sentry-sdk
```

Add to settings.py:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] File upload validation
- [ ] CSRF protection enabled
- [ ] XSS protection enabled
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Backup system in place

## Support

For issues or questions:
- Check logs first
- Review WaafiPay documentation
- Contact support@your-domain.com
