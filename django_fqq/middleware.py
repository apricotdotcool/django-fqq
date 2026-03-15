from django_fqq.schema import clear_schema, set_schema


class SchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # TBD: determine schema from request (e.g. subdomain, header, etc.)
        schema = self._get_schema(request)
        if schema:
            set_schema(schema)
        try:
            return self.get_response(request)
        finally:
            clear_schema()

    def _get_schema(self, request):
        """Override this method or replace with your own logic."""
        return None
