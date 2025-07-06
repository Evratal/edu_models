from django.test import TestCase
from edu_modules.models import EducationalModule


class ModuleSignalsTest(TestCase):
    def test_manual_order_preserved(self):
        module = EducationalModule.objects.create(title="Модуль", order=10)
        self.assertEqual(module.order, 10)
