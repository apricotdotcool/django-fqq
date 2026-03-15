import pytest
from django.conf import settings

from django_fqq.schema import clear_schema, get_schema, query_schema, set_schema


@pytest.fixture(autouse=True)
def schema_cleanup():
    yield
    clear_schema()


def test_get_schema_default():
    assert get_schema() is None


def test_set_and_get_schema():
    set_schema("tenant1")
    assert get_schema() == "tenant1"


def test_clear_schema():
    set_schema("tenant1")
    clear_schema()
    assert get_schema() is None


def test_query_schema_sets_and_clears():
    assert get_schema() is None
    with query_schema("tenant1"):
        assert get_schema() == "tenant1"
    assert get_schema() is None


def test_query_schema_restores_previous():
    set_schema("tenant1")
    with query_schema("tenant2"):
        assert get_schema() == "tenant2"
    assert get_schema() == "tenant1"


def test_query_schema_restores_on_exception():
    set_schema("tenant1")
    with pytest.raises(RuntimeError):
        with query_schema("tenant2"):
            assert get_schema() == "tenant2"
            raise RuntimeError("boom")
    assert get_schema() == "tenant1"


def test_query_schema_clears_on_exception_no_previous():
    assert get_schema() is None
    with pytest.raises(RuntimeError):
        with query_schema("tenant1"):
            raise RuntimeError("boom")
    assert get_schema() is None


def test_query_schema_nested():
    with query_schema("tenant1"):
        assert get_schema() == "tenant1"
        with query_schema("tenant2"):
            assert get_schema() == "tenant2"
        assert get_schema() == "tenant1"
    assert get_schema() is None
