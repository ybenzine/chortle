import pytest


@pytest.mark.django_db
def test_django_settings_are_loaded():
    from django.conf import settings

    assert "core" in settings.INSTALLED_APPS
