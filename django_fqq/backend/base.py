from django.db.backends.postgresql.base import (
    DatabaseWrapper as PostgresqlDatabaseWrapper,
)

from django_fqq.backend.operations import DatabaseOperations


class DatabaseWrapper(PostgresqlDatabaseWrapper):
    ops_class = DatabaseOperations
