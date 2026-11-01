from django.apps import AppConfig


class IdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.identity"
    label = "identity"

    def ready(self) -> None:
        from common import tasks  # noqa: F401
