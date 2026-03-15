from contextlib import contextmanager
from contextvars import ContextVar

_schema_var: ContextVar[str | None] = ContextVar("fqq_schema", default=None)


def set_schema(schema: str) -> None:
    _schema_var.set(schema)


def get_schema() -> str | None:
    return _schema_var.get()


def clear_schema() -> None:
    _schema_var.set(None)


@contextmanager
def query_schema(schema: str):
    previous = get_schema()
    set_schema(schema)
    try:
        yield
    finally:
        if previous is not None:
            set_schema(previous)
        else:
            clear_schema()
