import os
import django
import pytest
from django.conf import settings
from django.db import connection

from edu_modules.models import EducationalModule


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

@pytest.fixture(autouse=True)
def reset_db(request):
    # Очищаем БД перед каждым тестом
    for model in EducationalModule.__subclasses__():
        model.objects.all().delete()
    # Сбрасываем последовательности (для PostgreSQL)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence")

def enable_db_access_for_all_tests(db):
    """Дает доступ к базе данных всем тестам"""
    pass