from django.apps import AppConfig

class UseraccessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'useraccess'

    def ready(self):
        import useraccess.signals
