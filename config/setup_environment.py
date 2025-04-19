# import os

# def setup_environment():
#     environment = os.environ.get('APP_ENVIRONMENT', 'production')
#     environment_supported = ['production', 'production']
#     if environment not in environment_supported:
#         raise Exception(f'Please set environment variable APP_ENV from {environment_supported}')

#     settings_mapping = {
#         'production': 'config.settings.production',
#         'local': 'config.settings.local',
#     }
    
#     os.environ['DJANGO_SETTINGS_MODULE'] = settings_mapping[environment]
    
#     # Print the environment and settings for confirmation
#     print(f"APP_ENVIRONMENT is set to: {environment}")
#     print(f"DJANGO_SETTINGS_MODULE set to: {os.environ['DJANGO_SETTINGS_MODULE']}")

# # setup_environment()












# config/setup_environment.py
from dotenv import load_dotenv
from pathlib import Path

def setup_environment():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
