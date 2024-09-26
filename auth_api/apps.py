from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_api"

    def ready(self) -> None:
        from . import signals

        return super().ready()
