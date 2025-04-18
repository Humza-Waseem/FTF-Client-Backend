from django.core.wsgi import get_wsgi_application
from config.setup_environment import setup_environment

# Set up the environment (this will set DJANGO_SETTINGS_MODULE)
setup_environment()

# Initialize the WSGI application
application = get_wsgi_application()
