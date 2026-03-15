import pytest

from django_fqq.backend.operations import DatabaseOperations
from django_fqq.schema import clear_schema, set_schema


@pytest.fixture(autouse=True)
def schema_cleanup():
    yield
    clear_schema()


@pytest.fixture
def ops():
    """Create a DatabaseOperations instance with known table names."""
    from django.db import connection

    ops = connection.ops
    # Ensure test tables are registered
    ops._table_names |= {"auth_user", "auth_group", "myapp_tenant_model"}
    return ops


def test_quote_name_regular_column(ops):
    result = ops.quote_name("id")
    assert result == '"id"'


def test_quote_name_table_with_schema(ops):
    set_schema("tenant1")
    result = ops.quote_name("myapp_tenant_model")
    assert result == '"tenant1"."myapp_tenant_model"'


def test_quote_name_table_no_schema(ops):
    result = ops.quote_name("myapp_tenant_model")
    assert result == '"myapp_tenant_model"'


def test_quote_name_already_quoted(ops):
    result = ops.quote_name('"auth_user"')
    assert result == '"auth_user"'


def test_quote_name_dot_separated(ops):
    set_schema("tenant1")
    result = ops.quote_name("myschema.mytable")
    assert result == '"myschema"."mytable"'


def test_quote_name_non_table_unchanged(ops):
    result = ops.quote_name("not_a_table")
    assert result == '"not_a_table"'


def test_quote_name_schema_switches(ops):
    set_schema("a")
    result_a = ops.quote_name("myapp_tenant_model")
    assert result_a == '"a"."myapp_tenant_model"'

    set_schema("b")
    result_b = ops.quote_name("myapp_tenant_model")
    assert result_b == '"b"."myapp_tenant_model"'


def test_quote_name_shared_table_ignores_schema(ops):
    """Shared app tables always use 'public' regardless of current schema."""
    ops._shared_table_names |= {"auth_user"}
    set_schema("tenant1")
    result = ops.quote_name("auth_user")
    assert result == '"public"."auth_user"'


def test_quote_name_shared_table_without_schema_set(ops):
    """Shared app tables are not schema-qualified when no schema is set."""
    ops._shared_table_names |= {"auth_user"}
    result = ops.quote_name("auth_user")
    assert result == '"auth_user"'
