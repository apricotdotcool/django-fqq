from django.db.backends.postgresql.operations import (
    DatabaseOperations as PostgresqlDatabaseOperations,
)

from django_fqq.schema import get_schema


class DatabaseOperations(PostgresqlDatabaseOperations):
    _table_names: set[str] = set()
    _shared_table_names: set[str] = set()

    def quote_name(self, name):

        schema = get_schema()
        if not schema:
            return super().quote_name(name)

        if name.startswith('"'):
            return name

        if "." in name:
            parts = name.split(".")
            quote = super().quote_name
            return ".".join(quote(part) for part in parts)

        if name in self._table_names:
            if name in self._shared_table_names:
                schema = "public"
            return super().quote_name(schema) + "." + super().quote_name(name)

        return super().quote_name(name)
