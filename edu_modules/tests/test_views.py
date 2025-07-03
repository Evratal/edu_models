from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from edu_modules.models import EducationalModule

class EducationalModuleViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            username='admin',
            password='testpass'
        )
        cls.user = get_user_model().objects.create_user(
            username='user',
            password='testpass'
        )
        cls.module = EducationalModule.objects.create(
            order=1,
            title="Test Module",
            description="Description"
        )


    def test_toggle_active_action(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('educationalmodule-activate', args=[self.module.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.module.refresh_from_db()
        self.assertFalse(self.module.is_active)