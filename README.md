# django-fqq

Generate schema-prefixed table names with the Django ORM.

django-fqq provides a custom database backend that wraps Django's built-in PostgreSQL backend. It overrides `quote_name` to prepend the active schema to table names — so `"my_table"` becomes `"my_schema"."my_table"` automatically. No changes to your models or queries required.

django-fqq does not modify queries if `set_schema` has not been called or has been set to a falsy value (e.g. None or "").

## Installation

```bash
pip install django-fqq
```

## Configuration

### 1. Set the database backend

```python
DATABASES = {
    "default": {
        "ENGINE": "django_fqq.backend",
        "NAME": "your_db",
        # ... other options
    }
}
```

### 2. Add the app

```python
INSTALLED_APPS = [
    # ...
    "django_fqq",
]
```

### 3. Configure shared apps (optional)

Apps listed in `FQQ_SHARED_APPS` will always use the `public` schema, regardless of the active schema.

```python
FQQ_SHARED_APPS = ["auth", "contenttypes"]
```

### 4. Add the middleware (optional)

```python
MIDDLEWARE = [
    "django_fqq.middleware.SchemaMiddleware",
    # ...
]
```

Subclass `SchemaMiddleware` and override `_get_schema(request)` to resolve the schema from the request (e.g. from subdomain, header, or URL).

## Usage

### Setting the schema manually

```python
from django_fqq.schema import set_schema, clear_schema

set_schema("my_schema")
# All queries now target the "my_schema" schema
# ...
clear_schema()
```

### In a middleware or view

```python
from django_fqq.middleware import SchemaMiddleware

class MySchemaMiddleware(SchemaMiddleware):
    def _get_schema(self, request):
        host = request.get_host().split(".")[0]
        return host
```

### Using a context manager

`query_schema` sets the schema for the duration of a block and restores the previous state on exit.

```python
from django_fqq.schema import query_schema

with query_schema("my_schema"):
    # All queries target "my_schema"
    ...
# Schema is restored to its previous value (or cleared if none was set)
```

Nesting is supported — each level restores the schema that was active before it:

```python
from django_fqq.schema import set_schema, query_schema

set_schema("schema_a")

with query_schema("schema_b"):
    # queries target "schema_b"
    with query_schema("schema_c"):
        # queries target "schema_c"
        ...
    # back to "schema_b"

# back to "schema_a"
```

### Context-safe

Schema state is stored in a `ContextVar`, so it's safe across concurrent async requests and threads.

## Development

Requires Python 3.12+ and Django 6.0+.

```bash
uv sync
uv run pytest
```

## License

MIT
