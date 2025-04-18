from config.settings.base import *
import os
from .base import *
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
load_dotenv(dotenv_path=Path('.env'))
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = [ 'web-production-40c0.up.railway.app', 
#     'localhost',                         
#     '127.0.0.1'  ]
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'web-production-76282.up.railway.app']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


# POSTGRES_LOCALLY = True
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': os.environ.get('DB_NAME'),
    #     'USER': os.environ.get('DB_USER'),
    #     'PASSWORD': os.environ.get('DB_PASSWORD'),
    #     'HOST': os.environ.get('DB_HOST', 'localhost'),
    #     'PORT': os.environ.get('DB_PORT', '5432'),
    # }
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL")
    )
}
   # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }

DEBUG = False