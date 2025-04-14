release: python manage.py migrate
web: gunicorn config.wsgi:application --workers=2 --threads=4 --timeout 120 --max-requests 1000 --max-requests-jitter 50 --bind 0.0.0.0:$PORT