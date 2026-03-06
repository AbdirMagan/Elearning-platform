"""
Django settings for elearning project.
"""

import os

from decouple import config

from pathlib import Path
from pathlib import Path
from decouple import config, Csv
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-1234567890')
# DEBUG = config('DEBUG', default=True, cast=bool)
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,MaganH.pythonanywhere.com', cast=Csv())
DEBUG=False
ALLOWED_HOSTS=['*']
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'users.apps.UsersConfig',
    'courses.apps.CoursesConfig',
    'payments.apps.PaymentsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.SingleDeviceLoginMiddleware',  # Single device login
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'elearning.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'elearning.wsgi.application'

# # Database
# # PostgreSQL for production, SQLite for development
# DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3'),
#         conn_max_age=600,
#         conn_health_checks=True,
#     )
# }

# # For PostgreSQL specifically
# if 'postgresql' in DATABASES['default']['ENGINE'] or 'postgres' in DATABASES['default']['ENGINE']:
#     DATABASES['default']['OPTIONS'] = {
#         'connect_timeout': 10,
#     }
#New connection to to PostgreSQL database using dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default=f'sqlite:///{BASE_DIR}/db.sqlite3'  # fallback for development
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
# Example DATABASE_URL for reference:
# postgresql://postgres:bhXOSSDPOjznEiYkjdicIDdtZwyZqbHx@postgres.railway.internal:5432/railway
# PostgreSQL-specific options
# if DATABASES['default']['ENGINE'].startswith('django.db.backends.postgresql'):
#     DATABASES['default']['OPTIONS'] = {
#         'connect_timeout': 10,
#     }
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Authentication
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'courses:home'
LOGOUT_REDIRECT_URL = 'courses:home'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# WaafiPay Configuration
WAAFIPAY_MERCHANT_ID = config('WAAFIPAY_MERCHANT_ID', default='')
WAAFIPAY_API_USER_ID = config('WAAFIPAY_API_USER_ID', default='')
WAAFIPAY_API_KEY = config('WAAFIPAY_API_KEY', default='')
WAAFIPAY_MODE = config('WAAFIPAY_MODE', default='sandbox')  # 'sandbox' or 'production'
WAAFIPAY_CALLBACK_URL = config('WAAFIPAY_CALLBACK_URL', default='http://localhost:8000/payments/callback/')

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='AbadirHassan10@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='4711705@Ab.')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='AbadirHassan10@gmail.com')
SERVER_EMAIL = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
SITE_URL = config('SITE_URL', default='https://MaganH.pythonanywhere.com')

# Trusted origins for CSRF when running in production. Can be overridden via env var.
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://MaganH.pythonanywhere.com', cast=Csv())

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# Messages Framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 MB

# Allowed file extensions for uploads
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
ALLOWED_MATERIAL_EXTENSIONS = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip']

# Celery Configuration (Optional - for async tasks)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Sifalo Pay Configuration
SIFALO_USERNAME = config('SIFALO_USERNAME', default='')
SIFALO_PASSWORD = config('SIFALO_PASSWORD', default='')
SIFALO_MODE = config('SIFALO_MODE', default='sandbox')  # 'sandbox' or 'production'
SIFALO_CALLBACK_URL = config('SIFALO_CALLBACK_URL', default='http://localhost:8000/payments/callback/')
SIFALO_API_KEY = config('SIFALO_API_KEY', default='')
SIFALO_MERCHANT_ID = config('SIFALO_MERCHANT_ID', default='')
