import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.sql import DeleteQuery, InsertQuery, UpdateQuery

from django_fqq.schema import clear_schema, set_schema


@pytest.fixture(autouse=True)
def schema_cleanup():
    yield
    clear_schema()


# --- Tenant (non-shared) app: contenttypes ---


def test_select_query_has_schema():
    set_schema("tenant1")
    sql = str(ContentType.objects.all().query)
    assert '"tenant1"."django_content_type"' in sql


def test_select_query_no_schema():
    sql = str(ContentType.objects.all().query)
    assert '"django_content_type"' in sql
    assert '"public"."django_content_type"' not in sql


def test_filter_query_has_schema():
    set_schema("tenant1")
    sql = str(ContentType.objects.filter(pk=1).query)
    assert '"tenant1"."django_content_type"' in sql


def test_schema_switching_between_queries():
    set_schema("alpha")
    sql_alpha = str(ContentType.objects.all().query)
    assert '"alpha"."django_content_type"' in sql_alpha

    set_schema("beta")
    sql_beta = str(ContentType.objects.all().query)
    assert '"beta"."django_content_type"' in sql_beta


def test_delete_query_has_schema():
    set_schema("tenant1")
    dq = DeleteQuery(ContentType)
    sql = str(dq)
    assert '"tenant1"."django_content_type"' in sql


def test_delete_query_no_schema():
    dq = DeleteQuery(ContentType)
    sql = str(dq)
    assert '"django_content_type"' in sql
    assert '"public"."django_content_type"' not in sql


def test_update_query_has_schema():
    set_schema("tenant1")
    uq = UpdateQuery(ContentType)
    uq.add_update_values({"app_label": "test"})
    sql = str(uq)
    assert '"tenant1"."django_content_type"' in sql


def test_update_query_no_schema():
    uq = UpdateQuery(ContentType)
    uq.add_update_values({"app_label": "test"})
    sql = str(uq)
    assert '"django_content_type"' in sql
    assert '"public"."django_content_type"' not in sql


def test_insert_query_has_schema():
    set_schema("tenant1")
    iq = InsertQuery(ContentType)
    obj = ContentType(app_label="test", model="testmodel")
    iq.insert_values(ContentType._meta.local_concrete_fields, [obj])
    compiler = iq.get_compiler("default")
    sql, _ = compiler.as_sql()[0]
    assert '"tenant1"."django_content_type"' in sql


def test_insert_query_no_schema():
    iq = InsertQuery(ContentType)
    obj = ContentType(app_label="test", model="testmodel")
    iq.insert_values(ContentType._meta.local_concrete_fields, [obj])
    compiler = iq.get_compiler("default")
    sql, _ = compiler.as_sql()[0]
    assert '"django_content_type"' in sql
    assert '"public"."django_content_type"' not in sql


# --- Shared app: auth ---


def test_shared_app_always_uses_public_schema():
    set_schema("tenant1")
    sql = str(User.objects.all().query)
    assert '"public"."auth_user"' in sql


def test_shared_app_ignores_schema_switch():
    set_schema("alpha")
    sql_alpha = str(User.objects.all().query)
    assert '"public"."auth_user"' in sql_alpha

    set_schema("beta")
    sql_beta = str(User.objects.all().query)
    assert '"public"."auth_user"' in sql_beta


def test_shared_delete_uses_public_schema():
    set_schema("tenant1")
    dq = DeleteQuery(User)
    sql = str(dq)
    assert '"public"."auth_user"' in sql


def test_shared_update_uses_public_schema():
    set_schema("tenant1")
    uq = UpdateQuery(User)
    uq.add_update_values({"username": "test"})
    sql = str(uq)
    assert '"public"."auth_user"' in sql


def test_shared_insert_uses_public_schema():
    set_schema("tenant1")
    iq = InsertQuery(User)
    obj = User(username="test")
    iq.insert_values(User._meta.local_concrete_fields, [obj])
    compiler = iq.get_compiler("default")
    sql, _ = compiler.as_sql()[0]
    assert '"public"."auth_user"' in sql
