from django.apps import AppConfig


class authConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.userauth'
    def ready(self):
        import apps.userauth.signals  # This imports your signalsh:\FTF_Project\django-boilerplate\api\backends.pyh:\FTF_Project\django-boilerplate\api\backends.py