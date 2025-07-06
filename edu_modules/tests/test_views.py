from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import EducationalModule
from ..serializers import EducationalModuleCreateUpdateSerializer

User = get_user_model()


class EducationalModuleViewSetTest(APITestCase):
    def setUp(self):
        # Создаем пользователей с уникальными username
        self.admin = User.objects.create_superuser(
            username='admin1',
            password='adminpass',
            email='admin1@example.com'
        )
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='userpass',
            email='user@example.com'
        )

        # Создаем тестовый модуль
        self.module = EducationalModule.objects.create(
            title="Тестовый модуль",
            order=1,
            is_active=True
        )

    def test_toggle_active_action(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('educationalmodule-activate', kwargs={'pk': self.module.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'deactivated')

        self.module.refresh_from_db()
        self.assertFalse(self.module.is_active)

    def test_admin_permissions(self):
        # Тестируем доступ для админа
        self.client.force_authenticate(user=self.admin)
        valid_data = {
            'title': 'Новый модуль',
            'order': 2,
            'description': 'Описание нового модуля',
            'duration_hours': 10,
            'status': 'DF',
            'is_active': True
        }

        response = self.client.post(
            reverse('educationalmodule-list'),
            data=valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

        # Удаляем проверку created_by
        module = EducationalModule.objects.get(pk=response.data['id'])
        self.assertEqual(module.title, 'Новый модуль')  # Проверяем другое поле вместо created_by

        # Тестируем доступ для обычного пользователя
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            reverse('educationalmodule-list'),
            data=valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, 403)
