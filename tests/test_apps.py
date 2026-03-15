from django_fqq.backend.operations import DatabaseOperations


def test_table_names_populated():
    assert "auth_user" in DatabaseOperations._table_names
    assert "auth_group" in DatabaseOperations._table_names


def test_table_names_contains_content_type():
    assert "django_content_type" in DatabaseOperations._table_names


def test_shared_table_names_populated():
    """Auth tables are in _shared_table_names because FQQ_SHARED_APPS=["auth"]."""
    assert "auth_user" in DatabaseOperations._shared_table_names
    assert "auth_group" in DatabaseOperations._shared_table_names


def test_non_shared_app_not_in_shared_tables():
    """contenttypes is not in FQQ_SHARED_APPS, so its tables are not shared."""
    assert "django_content_type" not in DatabaseOperations._shared_table_names
