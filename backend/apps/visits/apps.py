from django.apps import AppConfig


class VisitsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visits"

    def ready(self):
        from . import signals  # noqa: F401
