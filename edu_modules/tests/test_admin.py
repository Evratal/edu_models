from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from ..admin import EducationalModuleAdmin
from ..models import EducationalModule

User = get_user_model()


class EducationalModuleAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = EducationalModuleAdmin(EducationalModule, self.site)
        self.user = User.objects.create_superuser(
            username='admin',
            password='adminpass'
        )
        self.module = EducationalModule.objects.create(
            title="Тестовый модуль",
            description="Описание тестового модуля",
            order=1,
            duration_hours=10
        )
        self.factory = RequestFactory()

    def test_list_display(self):
        """Проверка отображаемых полей в списке"""
        expected_fields = [
            'id', 'order', 'title', 'status_badge',
            'short_description', 'created_at', 'duration_info',
            'actions_column'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)

    def test_export_as_csv_action(self):
        """Тестирование действия экспорта в CSV"""
        request = self.factory.get('/admin/edu_modules/educationalmodule/')
        request.user = self.user

        # Создаем QuerySet с одним модулем
        queryset = EducationalModule.objects.filter(pk=self.module.pk)

        # Вызываем действие экспорта
        response = self.admin.export_as_csv(request, queryset)

        # Проверяем результат
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('modules_export.csv', response['Content-Disposition'])

        # Проверяем содержимое CSV
        content = response.content.decode('utf-8')
        self.assertIn('ID,Title,Status,Created At', content)
        self.assertIn('Тестовый модуль', content)

    def test_custom_methods(self):
        """Тестирование кастомных методов отображения"""
        # Проверка short_description
        self.assertEqual(
            self.admin.short_description(self.module),
            "Описание тестового модуля"  # Описание <50 символов
        )

        # Проверка duration_info
        self.assertEqual(
            self.admin.duration_info(self.module),
            "10 часов (2 дн.)"
        )

        # Проверка status_badge (базовый случай)
        self.module.status = 'DF'
        badge_html = self.admin.status_badge(self.module)
        self.assertIn('Черновик', badge_html)
        self.assertIn('background-color: gray', badge_html)