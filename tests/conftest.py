import django
from django.conf import settings


def pytest_configure():
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django_fqq.backend",
                "NAME": "test_fqq",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_fqq",
        ],
        FQQ_SHARED_APPS=["auth"],
    )
    django.setup()
