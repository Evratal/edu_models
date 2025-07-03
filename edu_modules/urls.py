from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EducationalModuleViewSet

router = DefaultRouter()
router.register(r'educational-modules', EducationalModuleViewSet, basename='educationalmodule')

urlpatterns = [
    path('', include(router.urls)),
]
