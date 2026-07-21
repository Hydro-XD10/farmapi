from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'tasks'

    def ready(self):
        # Connect the cost -> expense-transaction sync signal.
        from . import signals  # noqa: F401
