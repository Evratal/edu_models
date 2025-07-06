from rest_framework.test import APITestCase, APIRequestFactory
from django.contrib.auth import get_user_model
from edu_modules.permission import IsAdminOrReadOnly


class IsAdminOrReadOnlyTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminOrReadOnly()
        self.admin = get_user_model().objects.create_superuser(
            username='admin',
            password='testpass'
        )
        self.user = get_user_model().objects.create_user(
            username='user',
            password='testpass'
        )

    def test_has_permission_safe_methods(self):
        request = self.factory.get('/')
        request.user = self.user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_unsafe_methods_admin(self):
        request = self.factory.post('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_unsafe_methods_user(self):
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(self.permission.has_permission(request, None))
