from django.apps import AppConfig

class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'
    label = 'engine'

    def ready(self):
        import engine.signals

        