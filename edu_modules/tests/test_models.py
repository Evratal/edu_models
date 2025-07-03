from django.test import TestCase
from django.core.exceptions import ValidationError
from edu_modules.models import EducationalModule


class EducationalModuleModelTest(TestCase):
    def setUp(self):
        self.module = EducationalModule.objects.create(
            order=1,
            title="Тестовый модуль",
            description="Описание тестового модуля"
        )

    def test_module_creation(self):
        self.assertEqual(self.module.title, "Тестовый модуль")
        self.assertEqual(self.module.status, EducationalModule.ModuleStatus.DRAFT)
        self.assertTrue(self.module.is_active)

    def test_order_validation(self):
        with self.assertRaises(ValidationError):
            module = EducationalModule(order=0, title="Неверный порядок")
            module.full_clean()

    def test_string_representation(self):
        self.assertEqual(str(self.module), "1. Тестовый модуль")

    def test_short_description_property(self):
        self.module.description = "a" * 150
        self.assertEqual(len(self.module.short_description), 103)  # 100 + '...'

    def test_duration_days_calculation(self):
        self.module.duration_hours = 10
        self.assertEqual(self.module.duration_days, 2)
