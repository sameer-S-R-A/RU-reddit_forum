from django.apps import AppConfig


class RedditForumConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reddit_forum"

    def ready(self):
        from . import signals  # noqa: F401
