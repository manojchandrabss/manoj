from django.apps import AppConfig


class MentionsAppDefaultConfig(AppConfig):
    """
    Default configuration for Mentions app
    """

    name = 'apps.mentions'
    verbose_name = 'Mentions App'

    def ready(self):
        """Import signals on app ready state
        """
        from . import signals                               # flake8: noqa
