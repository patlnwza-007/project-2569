from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = 'M1 · บัญชีผู้ใช้'

    def ready(self):
        from . import signals  # noqa: F401
