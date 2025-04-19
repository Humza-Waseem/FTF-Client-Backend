# # config/wsgi.py
# import os
# from config.setup_environment import setup_environment
# setup_environment()  # ← MUST come before any Django import

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()


import os
from config.setup_environment import setup_environment
setup_environment()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
