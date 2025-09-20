from django.apps import AppConfig


class SitemonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sitemonitor'

    def ready(self):
        # Place for signals if needed later
        pass
