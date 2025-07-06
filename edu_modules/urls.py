from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import EducationalModuleViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'educational-modules', EducationalModuleViewSet, basename='educationalmodule')

urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),

    # OpenAPI Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI Documentation
    path('api/docs/', SpectacularSwaggerView.as_view(
        url_name='schema',
        template_name='swagger-ui.html',
        title='Educational Modules API'
    ), name='swagger-ui'),

    # ReDoc Documentation
    path('api/redoc/', SpectacularRedocView.as_view(
        url_name='schema',
        title='Educational Modules API Documentation'
    ), name='redoc'),
]
