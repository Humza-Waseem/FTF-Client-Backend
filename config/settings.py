import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# --------------------------------------------------
# Environment
# --------------------------------------------------
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')  # 'local' or 'production'
DEBUG = ENVIRONMENT == 'local'

# --------------------------------------------------
# Security
# --------------------------------------------------
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
# CSRF_TRUSTED_ORIGINS must include scheme (http:// or https://)
raw_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [u.strip() for u in raw_csrf.split(',') if u.strip().startswith(('http://', 'https://'))]

# --------------------------------------------------
# Applications
# --------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]
THIRD_PARTY_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.apple',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_rest_passwordreset',
    'django_password_validators',
    'django_password_validators.password_history',
]
PROJECT_APPS = [
    'apps.userauth',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# --------------------------------------------------
# Middleware
# --------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]
if not DEBUG:
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
MIDDLEWARE += [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# --------------------------------------------------
# URLs & WSGI/ASGI
# --------------------------------------------------
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# --------------------------------------------------
# Templates
# --------------------------------------------------
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

# --------------------------------------------------
# Database
# --------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# --------------------------------------------------
# Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# Static & Media
# --------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --------------------------------------------------
# Sessions
# --------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'

# --------------------------------------------------
# Auth & Allauth
# --------------------------------------------------
AUTH_USER_MODEL = 'userauth.User'
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'apps.userauth.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# --------------------------------------------------
# REST Framework
# --------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# --------------------------------------------------
# JWT
# --------------------------------------------------
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# --------------------------------------------------
# Social Account Providers
# --------------------------------------------------
SOCIALACCOUNT_PROVIDERS = {
    'google': {'SCOPE': ['profile', 'email'], 'AUTH_PARAMS': {'access_type': 'online'}},
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': ['id', 'first_name', 'last_name', 'name', 'picture'],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
    },
    'apple': {
        'APPS': [{
            'client_id': os.getenv('APPLE_CLIENT_ID'),
            'secret': os.getenv('APPLE_SECRET'),
            'key': os.getenv('APPLE_KEY'),
            'settings': {'certificate_key': os.getenv('APPLE_CERT')}
        }]
    },
}

# --------------------------------------------------
# Email (development)
# --------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --------------------------------------------------
# Login/Logout
# --------------------------------------------------
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/apps/userauth/register'

# --------------------------------------------------
# Caches & API Configs
# --------------------------------------------------
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'unique-snowflake'}
}
API_CONFIGS = {
    'NUTRITIONIX': {'APP_ID': os.getenv('NUTRITIONIX_APP_ID'), 'APP_KEY': os.getenv('NUTRITIONIX_APP_KEY'), 'BASE_URL': 'https://trackapi.nutritionix.com/v2'},
    'MINDBODY': {'API_KEY': os.getenv('MINDBODY_API_KEY'), 'SITE_ID': os.getenv('MINDBODY_SITE_ID'), 'BASE_URL': os.getenv('MINDBODY_BASE_URL')},
    'INBODY': {'API_KEY': os.getenv('INBODY_API_KEY'), 'ACCOUNT': os.getenv('INBODY_ACCOUNT'), 'BASE_URL': 'https://api.inbody.com'},
    'PERKVILLE': {'CLIENT_ID': os.getenv('PERKVILLE_CLIENT_ID'), 'CLIENT_SECRET': os.getenv('PERKVILLE_CLIENT_SECRET'), 'REDIRECT_URI': os.getenv('PERKVILLE_REDIRECT_URI'), 'BASE_URL': os.getenv('PERKVILLE_BASE_URL'), 'PERKVILLE_TOKEN_URL': os.getenv('PERKVILLE_TOKEN_URL'), 'PERKVILLE_AUTHORIZE_URL': os.getenv('PERKVILLE_AUTHORIZE_URL'), 'PERKVILLE_SCOPES': os.getenv('PERKVILLE_SCOPES')},
}