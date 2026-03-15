import pytest
from django.db import models
from django.db.models import Count, Exists, OuterRef, Subquery
from django.db.models.expressions import RawSQL

from django_fqq.backend.operations import DatabaseOperations
from django_fqq.schema import clear_schema, set_schema


class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "testapp"
        db_table = "testapp_author"


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        app_label = "testapp"
        db_table = "testapp_book"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book)

    class Meta:
        app_label = "testapp"
        db_table = "testapp_tag"


TABLE_NAMES = {"testapp_author", "testapp_book", "testapp_tag", "testapp_tag_books"}


@pytest.fixture(autouse=True)
def schema_cleanup():
    yield
    clear_schema()


@pytest.fixture(autouse=True)
def register_tables():
    DatabaseOperations._table_names.update(TABLE_NAMES)
    yield
    DatabaseOperations._table_names.difference_update(TABLE_NAMES)


# --- JOINs ---


def test_select_related_join_qualifies_both_tables():
    set_schema("tenant1")
    sql = str(Book.objects.select_related("author").query)
    assert 'JOIN "tenant1"."testapp_author"' in sql
    assert '"tenant1"."testapp_book"' in sql


def test_fk_filter_qualifies_joined_table():
    set_schema("tenant1")
    sql = str(Book.objects.filter(author__name="test").query)
    assert 'JOIN "tenant1"."testapp_author"' in sql
    assert '"tenant1"."testapp_book"' in sql


def test_join_no_schema():
    sql = str(Book.objects.select_related("author").query)
    assert '"testapp_book"' in sql
    assert '"testapp_author"' in sql
    assert "tenant" not in sql


# --- Many-to-many ---


def test_m2m_filter_qualifies_all_three_tables():
    set_schema("tenant1")
    sql = str(Tag.objects.filter(books__title="test").query)
    assert '"tenant1"."testapp_tag"' in sql
    assert '"tenant1"."testapp_tag_books"' in sql
    assert '"tenant1"."testapp_book"' in sql


def test_m2m_no_schema():
    sql = str(Tag.objects.filter(books__title="test").query)
    assert '"testapp_tag"' in sql
    assert '"testapp_tag_books"' in sql
    assert '"testapp_book"' in sql
    assert "tenant" not in sql


# --- Aggregations ---


def test_count_annotation_qualifies_table():
    set_schema("tenant1")
    sql = str(Book.objects.values("author").annotate(count=Count("id")).query)
    assert '"tenant1"."testapp_book"' in sql


def test_count_annotation_no_schema():
    sql = str(Book.objects.values("author").annotate(count=Count("id")).query)
    assert '"testapp_book"' in sql
    assert "tenant" not in sql


# --- Subqueries ---


def test_subquery_qualifies_outer_and_inner_tables():
    set_schema("tenant1")
    inner = Subquery(Book.objects.values("author_id"))
    sql = str(Author.objects.filter(pk__in=inner).query)
    assert '"tenant1"."testapp_author"' in sql
    assert '"tenant1"."testapp_book"' in sql


def test_exists_subquery_qualifies_both_tables():
    set_schema("tenant1")
    subq = Exists(Author.objects.filter(pk=OuterRef("author_id")))
    sql = str(Book.objects.filter(subq).query)
    assert '"tenant1"."testapp_book"' in sql
    assert '"tenant1"."testapp_author"' in sql


def test_subquery_no_schema():
    inner = Subquery(Book.objects.values("author_id"))
    sql = str(Author.objects.filter(pk__in=inner).query)
    assert '"testapp_author"' in sql
    assert '"testapp_book"' in sql
    assert "tenant" not in sql


# --- RawSQL expressions ---


def test_rawsql_annotation_qualifies_main_table():
    set_schema("tenant1")
    sql = str(Book.objects.annotate(custom=RawSQL("1", [])).query)
    assert '"tenant1"."testapp_book"' in sql


def test_rawsql_preserves_hand_written_sql():
    set_schema("tenant1")
    raw_fragment = '"some_other_table"."col"'
    sql = str(Book.objects.annotate(custom=RawSQL(raw_fragment, [])).query)
    assert '"tenant1"."testapp_book"' in sql
    # The hand-written fragment should pass through unchanged
    assert raw_fragment in sql


def test_extra_select_qualifies_main_table():
    set_schema("tenant1")
    sql = str(Book.objects.extra(select={"one": "1"}).query)
    assert '"tenant1"."testapp_book"' in sql
