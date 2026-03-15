import pytest
from django.http import HttpRequest, HttpResponse

from django_fqq.middleware import SchemaMiddleware
from django_fqq.schema import clear_schema, get_schema


@pytest.fixture(autouse=True)
def schema_cleanup():
    yield
    clear_schema()


def test_middleware_clears_schema_after_response():
    from django_fqq.schema import set_schema

    set_schema("leftover")

    def get_response(request):
        return HttpResponse("ok")

    middleware = SchemaMiddleware(get_response)
    middleware(HttpRequest())

    assert get_schema() is None


def test_middleware_clears_schema_on_exception():
    from django_fqq.schema import set_schema

    def get_response(request):
        raise ValueError("boom")

    class TestMiddleware(SchemaMiddleware):
        def _get_schema(self, request):
            return "tenant_error"

    middleware = TestMiddleware(get_response)

    with pytest.raises(ValueError):
        middleware(HttpRequest())

    assert get_schema() is None


def test_middleware_sets_schema():
    schema_during_request = None

    def get_response(request):
        nonlocal schema_during_request
        schema_during_request = get_schema()
        return HttpResponse("ok")

    class TestMiddleware(SchemaMiddleware):
        def _get_schema(self, request):
            return "tenant_mid"

    middleware = TestMiddleware(get_response)
    middleware(HttpRequest())

    assert schema_during_request == "tenant_mid"
    # Verify cleanup happened
    assert get_schema() is None
