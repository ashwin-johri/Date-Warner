from django.apps import AppConfig


class MyASDConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myASD'
    def ready(self):
        import myASD.signals
