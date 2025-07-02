from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EducationalModuleViewSet

router = DefaultRouter()
router.register(r'modules', EducationalModuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
