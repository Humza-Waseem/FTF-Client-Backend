
from pathlib import Path
import os
import environ
from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')
env = environ.Env()
# reading .env file
environ.Env.read_env(BASE_DIR.__str__() + '/.env')


env = environ.Env()
environ.Env.read_env() 
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    ##########   THIRD PARTY APPS    #########
    'django.contrib.sites',
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
    ###################   OUR APPS   ###################
    'apps.userauth',
    
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
THIRD_PARTY_APPS = []

PROJECT_APPS = [
    # 'apps.users'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    
]


SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'  # Or your preferred backend
SESSION_COOKIE_SECURE = False  # True in production
SESSION_COOKIE_SAMESITE = 'Lax'


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# AUTH USER 

# AUTH_USER_MODEL = 'users.User'
AUTH_USER_MODEL = 'userauth.User'


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}


AUTHENTICATION_BACKENDS = [
    'apps.userauth.backends.EmailBackend', # Path to the EmailBackend
    'django.contrib.auth.backends.ModelBackend',  # Default
    'allauth.account.auth_backends.AuthenticationBackend', #The backend for django-allauth

]
# Social Account Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',  # Set to 'js_sdk' to use the Facebook connect SDK
        # 'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        # 'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
        'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
    },
    "apple": {
        "APPS": [{
            # Your service identifier.
            "client_id": "your.service.id",

            # The Key ID (visible in the "View Key Details" page).
            "secret": "KEYID",

             # Member ID/App ID Prefix -- you can find it below your name
             # at the top right corner of the page, or it’s your App ID
             # Prefix in your App ID.
            "key": "MEMAPPIDPREFIX",

            "settings": {
                # The certificate you downloaded when generating the key.
                "certificate_key": """-----BEGIN PRIVATE KEY-----
s3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr
3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3
c3ts3cr3t
-----END PRIVATE KEY-----
"""
            }
        }]
    }
}
SITE_ID = 1  # Important for allauth
# Social Account Settings
ACCOUNT_LOGIN_METHODS = {'email'}  # Replaces ACCOUNT_AUTHENTICATION_METHOD
# ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  


#only for DEVELOPMENT
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'lalo.salamancaa00@gmail.com'  
EMAIL_HOST_PASSWORD = 'ijpb pmhx idit nxch'  
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # Use the same email as the sender




LOGIN_REDIRECT_URL = '/'  
LOGOUT_REDIRECT_URL = '/apps/userauth/register' 


# App Secret:220b0bb17f0131dba49428288fc6885e
#App ID: 3922625784619237
    # 691013845055-p186tvq8o8vi563s3r5hejfv9ols82lo.apps.googleusercontent.com

# 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
TIME_ZONE = 'Asia/Karachi'  # Example for Pakistan Time (UTC+5)
USE_TZ = True  # Important: This enables timezone awareness

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # In-memory cache for development
        'LOCATION': 'unique-snowflake',
    }
}



#?API Configurations
API_CONFIGS = {
    'NUTRITIONIX': {
        'APP_ID': os.getenv('NUTRITIONIX_APP_ID'),
        'APP_KEY': os.getenv('NUTRITIONIX_APP_KEY'),
        'BASE_URL': 'https://trackapi.nutritionix.com/v2'
    },
    'MINDBODY': {
        'API_KEY': os.getenv('MINDBODY_API_KEY'),
        'SITE_ID': os.getenv('MINDBODY_SITE_ID'),
        'BASE_URL': os.getenv('MINDBODY_BASE_URL')
    },
    'INBODY': {
        'API_KEY': os.getenv('INBODY_API_KEY'),
        'ACCOUNT': os.getenv('INBODY_ACCOUNT'),
        'BASE_URL': 'https://api.inbody.com'  # Example URL
    },
    'PERKVILLE': {
        'CLIENT_ID': os.getenv('PERKVILLE_CLIENT_ID'),
        'CLIENT_SECRET': os.getenv('PERKVILLE_CLIENT_SECRET'),
        'REDIRECT_URI': os.getenv('PERKVILLE_REDIRECT_URI'),
        'BASE_URL': os.getenv('PERKVILLE_BASE_URL'),
        'PERKVILLE_TOKEN_URL' : os.getenv('PERKVILLE_TOKEN_URL'),
        'PERKVILLE_AUTHORIZE_URL' : os.getenv('PERKVILLE_AUTHORIZE_URL'),
        'PERKVILLE_SCOPES': os.getenv('PERKVILLE_SCOPES')
   

    },
    
}

# Example usage:

# Validation
# for service, config in API_CONFIGS.items():
#     if not all(config.values()):
#         raise ValueError(f"Missing configuration for {service} API")
    
    
    
STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # DEPLOYMENT PURPOSES
# CSRF_TRUSTED_ORIGINS= [ "https://web-production-40c0.up.railway.app/","https://web-production-76282.up.railway.app/", "web-production-40c0.up.railway.app",  
#     "localhost",                         
#     "127.0.0.1" ] 


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},  # You can increase this to 12 for better security
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
