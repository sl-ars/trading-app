"""
Django settings for trading_app project.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from django.utils.log import DEFAULT_LOGGING
import drf_spectacular
# Check if running inside Docker
DOCKER_MODE = os.getenv('DOCKERIZED')

# === BASE DIRECTORY === #
BASE_DIR = Path(__file__).resolve().parent.parent

# === ENVIRONMENT VARIABLES === #
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# === SECURITY SETTINGS === #
SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# === FRONTEND URL === #
if DEBUG:
    FRONTEND_URL = "http://localhost:5173"
else:
    FRONTEND_URL = env.str("FRONTEND_URL")

# === APPLICATION CONFIGURATION === #
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    'storages',
    'channels',
    'users',
    'products',
    'trading',
    'sales',
    'analytics',
    'notifications',
    'webhooks'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# === CORS SETTINGS (SECURE FOR PRODUCTION) === #
if DEBUG:
    CORS_ALLOWED_ORIGINS  = ["http://localhost:5173"]
else:
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
        "http://localhost:5173"
    ])

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# === URL CONFIGURATION === #
ROOT_URLCONF = 'trading_app.urls'

# === TEMPLATES === #
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
            ],
        },
    },
]

WSGI_APPLICATION = 'trading_app.wsgi.application'
ASGI_APPLICATION = 'trading_app.asgi.application'

# === DATABASE CONFIGURATION === #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='trading_db'),
        'USER': env('POSTGRES_USER', default='trading_user'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='trading_password'),
        'HOST': env('POSTGRES_HOST', default='db' if DOCKER_MODE else 'localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
    }
}

# === REST FRAMEWORK CONFIGURATION === #
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema'
}

# === PASSWORD VALIDATION === #
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === INTERNATIONALIZATION === #
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === STATIC & MEDIA FILES (S3 CONFIGURATION) === #
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

# === SWAGGER SETTINGS === #
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter JWT token as "Bearer <your_token>"',
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

# === LOGIN SETTINGS === #
LOGIN_URL = "users/login/"
LOGIN_REDIRECT_URL = "users/profile/"
LOGOUT_REDIRECT_URL = "users/login/"

# === STRIPE PAYMENT SETTINGS === #
STRIPE_SECRET_KEY = env.str('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = env.str('STRIPE_PUBLIC_KEY')
STRIPE_WEBHOOK_SECRET = env.str('STRIPE_WEBHOOK_SECRET')

# === CHANNELS (WEBSOCKETS) === #
REDIS_HOST = "redis" if DOCKER_MODE else "127.0.0.1"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

# === CELERY === #
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"



# === JWT === #

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# === SENTRY Configuration === #
SENTRY_DSN = env.str("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            CeleryIntegration()
        ],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment="production" if not DEBUG else "development",
    )



LOGGING = DEFAULT_LOGGING.copy()
if not DEBUG:
    LOGGING.update(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{levelname} {asctime} {module} {message}",
                    "style": "{",
                },
                "simple": {
                    "format": "{levelname} {message}",
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "level": "CRITICAL",
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "verbose",
                },
                "sentry": {
                    "level": "ERROR",
                    "class": "sentry_sdk.integrations.logging.EventHandler",
                },
            },
            "loggers": {
                "django": {
                    "handlers": ["console", "sentry"],
                    "level": "ERROR",
                    "propagate": True,
                },
                "django.request": {
                    "handlers": ["sentry"],
                    "level": "ERROR",
                    "propagate": False,
                },
            },
        }
    )