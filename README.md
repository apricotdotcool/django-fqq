# django-fqq

Lightweight PostgreSQL schema-based multi-tenancy for Django.

django-fqq automatically qualifies table names with the appropriate PostgreSQL schema, routing queries to tenant-specific schemas using a simple `ContextVar`-based approach. Shared tables (like `auth`) stay in `public`, while tenant tables are directed to the active schema.

## How it works

django-fqq provides a custom database backend that wraps Django's built-in PostgreSQL backend. It overrides `quote_name` to prepend the active schema to table names — so `"my_table"` becomes `"tenant_schema"."my_table"` automatically. No changes to your models or queries required.

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

### 3. Configure shared apps

Apps listed in `FQQ_SHARED_APPS` will always use the `public` schema. Everything else uses the active tenant schema.

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

Subclass `SchemaMiddleware` and override `_get_schema(request)` to resolve the tenant schema from the request (e.g. from subdomain, header, or URL).

## Usage

### Setting the schema manually

```python
from django_fqq.schema import set_schema, clear_schema

set_schema("tenant_abc")
# All queries now target the "tenant_abc" schema
# ...
clear_schema()
```

### In a middleware or view

```python
from django_fqq.middleware import SchemaMiddleware

class MySchemaMiddleware(SchemaMiddleware):
    def _get_schema(self, request):
        # Resolve tenant from subdomain
        host = request.get_host().split(".")[0]
        return host
```

### Using a context manager

`query_schema` is a context manager that sets the schema for the duration of a block and automatically restores the previous state on exit. If a schema was already active, it is restored rather than cleared.

```python
from django_fqq.schema import query_schema

with query_schema("tenant_abc"):
    # All queries target "tenant_abc"
    ...
# Schema is restored to its previous value (or cleared if none was set)
```

It supports nesting — each level restores the schema that was active before it:

```python
from django_fqq.schema import set_schema, query_schema

set_schema("tenant_a")

with query_schema("tenant_b"):
    # queries target "tenant_b"
    with query_schema("tenant_c"):
        # queries target "tenant_c"
        ...
    # back to "tenant_b"

# back to "tenant_a"
```

The previous schema is also restored if an exception is raised inside the block.

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
