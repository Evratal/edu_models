from rest_framework.test import APITestCase
from rest_framework import serializers
from edu_modules.models import EducationalModule
from edu_modules.serializers import EducationalModuleCreateUpdateSerializer

class EducationalModuleSerializerTest(APITestCase):
    def setUp(self):
        self.module_data = {
            'order': 1,
            'title': 'Сериализованный модуль',
            'description': 'Описание'
        }

    def test_serializer_valid_data(self):
        serializer = EducationalModuleCreateUpdateSerializer(data=self.module_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_order(self):
        self.module_data['order'] = 0
        serializer = EducationalModuleCreateUpdateSerializer(data=self.module_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('order', serializer.errors)

    def test_serializer_admin_high_order(self):
        user = self.create_admin_user()
        self.module_data['order'] = 101
        serializer = EducationalModuleCreateUpdateSerializer(
            data=self.module_data,
            context={'request': self.create_request(user)}
        )
        self.assertTrue(serializer.is_valid())

    def create_admin_user(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_superuser(
            username='admin',
            password='testpass'
        )

    def create_request(self, user):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = user
        return request
