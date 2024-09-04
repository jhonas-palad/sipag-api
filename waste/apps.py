from django.apps import AppConfig


class WasteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "waste"

    def ready(self) -> None:
        from . import signal_handlers
