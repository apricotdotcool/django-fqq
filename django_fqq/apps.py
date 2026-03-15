from django.apps import AppConfig


class DjangoFqqConfig(AppConfig):
    name = "django_fqq"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from django.apps import apps
        from django.conf import settings
        from django.db import connections

        from django_fqq.backend.operations import DatabaseOperations

        shared_apps = set(getattr(settings, "FQQ_SHARED_APPS", []))

        table_names = set()
        shared_table_names = set()
        for model in apps.get_models():
            table = model._meta.db_table
            table_names.add(table)
            if model._meta.app_label in shared_apps:
                shared_table_names.add(table)

        DatabaseOperations._table_names = table_names
        DatabaseOperations._shared_table_names = shared_table_names

        for conn in connections.all():
            if isinstance(conn.ops, DatabaseOperations):
                conn.ops._table_names = table_names
                conn.ops._shared_table_names = shared_table_names
