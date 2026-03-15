from unittest.mock import patch

import pytest
from django.db import connection, models
from django.db.models import Index

from django_fqq.backend.operations import DatabaseOperations
from django_fqq.schema import clear_schema, set_schema


class TenantModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "testapp"
        db_table = "testapp_tenantmodel"


class TenantModelWithAge(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=0)

    class Meta:
        app_label = "testapp"
        db_table = "testapp_tenantmodel"


@pytest.fixture(autouse=True)
def schema_cleanup():
    yield
    clear_schema()


@pytest.fixture(autouse=True)
def register_table():
    DatabaseOperations._table_names.add("testapp_tenantmodel")
    yield
    DatabaseOperations._table_names.discard("testapp_tenantmodel")
    DatabaseOperations._table_names.discard("testapp_newname")


def _noop_compose_sql(sql, params, connection):
    """Substitute params into SQL without needing a real DB cursor."""
    if params:
        return sql % tuple(repr(p) for p in params)
    return sql


def _collect_sql(fn):
    """Run schema editor operation and return collected SQL statements."""
    with patch(
        "django.db.backends.postgresql.operations.mogrify", side_effect=_noop_compose_sql
    ):
        editor = connection.schema_editor(collect_sql=True, atomic=False)
        with editor:
            fn(editor)
        return editor.collected_sql


# --- CREATE TABLE ---


def test_create_table_has_schema():
    set_schema("tenant1")
    sqls = _collect_sql(lambda e: e.create_model(TenantModel))
    assert any('"tenant1"."testapp_tenantmodel"' in s for s in sqls)


def test_create_table_no_schema():
    sqls = _collect_sql(lambda e: e.create_model(TenantModel))
    assert any('"testapp_tenantmodel"' in s for s in sqls)
    assert not any('"public"."testapp_tenantmodel"' in s for s in sqls)


# --- DROP TABLE ---


def test_drop_table_has_schema():
    set_schema("tenant1")
    sqls = _collect_sql(lambda e: e.delete_model(TenantModel))
    assert any('"tenant1"."testapp_tenantmodel"' in s for s in sqls)


def test_drop_table_no_schema():
    sqls = _collect_sql(lambda e: e.delete_model(TenantModel))
    assert any('"testapp_tenantmodel"' in s for s in sqls)
    assert not any('"public"."testapp_tenantmodel"' in s for s in sqls)


# --- ADD COLUMN ---


def test_add_column_has_schema():
    set_schema("tenant1")
    field = TenantModelWithAge._meta.get_field("age")
    sqls = _collect_sql(lambda e: e.add_field(TenantModelWithAge, field))
    assert any('"tenant1"."testapp_tenantmodel"' in s for s in sqls)


def test_add_column_no_schema():
    field = TenantModelWithAge._meta.get_field("age")
    sqls = _collect_sql(lambda e: e.add_field(TenantModelWithAge, field))
    assert any('"testapp_tenantmodel"' in s for s in sqls)
    assert not any('"public"."testapp_tenantmodel"' in s for s in sqls)


# --- DROP COLUMN ---


def test_drop_column_has_schema():
    set_schema("tenant1")
    field = TenantModelWithAge._meta.get_field("age")
    sqls = _collect_sql(lambda e: e.remove_field(TenantModelWithAge, field))
    assert any('"tenant1"."testapp_tenantmodel"' in s for s in sqls)


# --- ADD INDEX ---


def test_add_index_has_schema():
    set_schema("tenant1")
    idx = Index(fields=["name"], name="testapp_tenantmodel_name_idx")
    sqls = _collect_sql(lambda e: e.add_index(TenantModel, idx))
    assert any('"tenant1"."testapp_tenantmodel"' in s for s in sqls)


def test_add_index_no_schema():
    idx = Index(fields=["name"], name="testapp_tenantmodel_name_idx")
    sqls = _collect_sql(lambda e: e.add_index(TenantModel, idx))
    assert any('"testapp_tenantmodel"' in s for s in sqls)
    assert not any('"public"."testapp_tenantmodel"' in s for s in sqls)


# --- RENAME TABLE ---


def test_rename_table_has_schema():
    set_schema("tenant1")
    DatabaseOperations._table_names.add("testapp_newname")
    sqls = _collect_sql(
        lambda e: e.alter_db_table(TenantModel, "testapp_tenantmodel", "testapp_newname")
    )
    assert any('"tenant1"."testapp_tenantmodel"' in s for s in sqls)


def test_rename_table_no_schema():
    DatabaseOperations._table_names.add("testapp_newname")
    sqls = _collect_sql(
        lambda e: e.alter_db_table(TenantModel, "testapp_tenantmodel", "testapp_newname")
    )
    assert any('"testapp_tenantmodel"' in s for s in sqls)
    assert not any('"public"."testapp_tenantmodel"' in s for s in sqls)


# --- Schema switching across operations ---


def test_schema_switch_between_operations():
    set_schema("alpha")
    sqls_alpha = _collect_sql(lambda e: e.create_model(TenantModel))
    assert any('"alpha"."testapp_tenantmodel"' in s for s in sqls_alpha)

    set_schema("beta")
    sqls_beta = _collect_sql(lambda e: e.create_model(TenantModel))
    assert any('"beta"."testapp_tenantmodel"' in s for s in sqls_beta)
