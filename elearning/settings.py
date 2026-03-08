"""
Django settings for elearning project.
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# ENVIRONMENT DETECTION
# ─────────────────────────────────────────────
# Automatically detect if running on Railway
ON_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ

# DEBUG: False on Railway, True locally unless overridden
DEBUG = config('DEBUG', default=not ON_RAILWAY, cast=bool)

# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-1234567890')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ─────────────────────────────────────────────
# DATABASE — SQLite locally, PostgreSQL on Railway
# ─────────────────────────────────────────────
_db_url = config('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3')

# Guard: prevent accidentally connecting to Railway's internal DB from local machine
if 'railway.internal' in _db_url and not ON_RAILWAY:
    import warnings
    warnings.warn(
        "\n\n⚠️  WARNING: DATABASE_URL points to 'railway.internal' but you're running locally.\n"
        "   Falling back to SQLite. Update your .env to use a local DB URL.\n",
        stacklevel=2
    )
    _db_url = f'sqlite:///{BASE_DIR}/db.sqlite3'

DATABASES = {
    'default': dj_database_url.config(
        default=_db_url,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# PostgreSQL-specific options
if 'postgresql' in DATABASES['default'].get('ENGINE', ''):
    DATABASES['default']['OPTIONS'] = {'connect_timeout': 10}

# ─────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'cloudinary_storage',
    'cloudinary',

    # Local
    'users.apps.UsersConfig',
    'courses.apps.CoursesConfig',
    'payments.apps.PaymentsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.SingleDeviceLoginMiddleware',
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

# ─────────────────────────────────────────────
# STATIC FILES (WhiteNoise)
# ─────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─────────────────────────────────────────────
# MEDIA FILES
# • Cloudinary when credentials are present (production/Railway)
# • Local filesystem when credentials are missing (development)
# ─────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY    = config('CLOUDINARY_API_KEY',    default='')
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')

USE_CLOUDINARY = all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET])

if USE_CLOUDINARY:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )

    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY':    CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }

    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL  = f'https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/'
    MEDIA_ROOT = ''  # Not used — Cloudinary handles storage

else:
    # Development: store media locally
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)

# ─────────────────────────────────────────────
# AUTH & MISC
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL     = 'users.CustomUser'
LOGIN_URL           = 'users:login'
LOGIN_REDIRECT_URL  = 'courses:home'
LOGOUT_REDIRECT_URL = 'courses:home'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK          = "bootstrap5"

# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────
# INTERNATIONALISATION
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
EMAIL_BACKEND     = config('EMAIL_BACKEND',     default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST        = config('EMAIL_HOST',        default='smtp.gmail.com')
EMAIL_PORT        = config('EMAIL_PORT',        default=587, cast=int)
EMAIL_USE_TLS     = config('EMAIL_USE_TLS',     default=True, cast=bool)
EMAIL_HOST_USER   = config('EMAIL_HOST_USER',   default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL',  default='noreply@yourdomain.com')
SERVER_EMAIL        = config('SERVER_EMAIL',        default=DEFAULT_FROM_EMAIL)
SITE_URL            = config('SITE_URL',            default='http://localhost:8000')

# ─────────────────────────────────────────────
# CSRF
# ─────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv()
)

# ─────────────────────────────────────────────
# SECURITY SETTINGS (production only)
# ─────────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT         = False  # Railway handles SSL termination
    SESSION_COOKIE_SECURE       = True
    CSRF_COOKIE_SECURE          = True
    SECURE_BROWSER_XSS_FILTER   = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS         = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD         = True
    X_FRAME_OPTIONS             = 'DENY'

# ─────────────────────────────────────────────
# MESSAGES
# ─────────────────────────────────────────────
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG:   'alert-info',
    messages.INFO:    'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR:   'alert-danger',
}

# ─────────────────────────────────────────────
# FILE UPLOADS
# ─────────────────────────────────────────────
FILE_UPLOAD_MAX_MEMORY_SIZE  = 100 * 1024 * 1024  # 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE  = 100 * 1024 * 1024  # 100 MB
ALLOWED_VIDEO_EXTENSIONS     = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
ALLOWED_MATERIAL_EXTENSIONS  = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip']

# ─────────────────────────────────────────────
# PAYMENT GATEWAYS
# ─────────────────────────────────────────────
WAAFIPAY_MERCHANT_ID  = config('WAAFIPAY_MERCHANT_ID',  default='')
WAAFIPAY_API_USER_ID  = config('WAAFIPAY_API_USER_ID',  default='')
WAAFIPAY_API_KEY      = config('WAAFIPAY_API_KEY',      default='')
WAAFIPAY_MODE         = config('WAAFIPAY_MODE',         default='sandbox')
WAAFIPAY_CALLBACK_URL = config('WAAFIPAY_CALLBACK_URL', default='http://localhost:8000/payments/callback/')

SIFALO_USERNAME     = config('SIFALO_USERNAME',     default='')
SIFALO_PASSWORD     = config('SIFALO_PASSWORD',     default='')
SIFALO_MODE         = config('SIFALO_MODE',         default='sandbox')
SIFALO_CALLBACK_URL = config('SIFALO_CALLBACK_URL', default='http://localhost:8000/payments/callback/')
SIFALO_API_KEY      = config('SIFALO_API_KEY',      default='')
SIFALO_MERCHANT_ID  = config('SIFALO_MERCHANT_ID',  default='')

# ─────────────────────────────────────────────
# CELERY (Optional)
# ─────────────────────────────────────────────
CELERY_BROKER_URL        = config('CELERY_BROKER_URL',    default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND    = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = TIME_ZONE