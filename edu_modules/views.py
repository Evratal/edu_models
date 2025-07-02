# flake8: noqa: E501

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission
from django_filters.rest_framework import DjangoFilterBackend

from .models import EducationalModule
from .serializers import EducationalModuleSerializer, EducationalModuleDetailSerializer
from .filters import EducationalModuleFilter


class IsAdminOrReadOnly(BasePermission):
    """Разрешение: редактирование только для админов, чтение для всех"""
    def has_permission(self, request, view):
        return (
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            request.user and
            request.user.is_staff
        )


class EducationalModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для образовательных модулей с расширенными функциями:
    - CRUD операции
    - Фильтрация и поиск
    - Кастомные действия
    """
    queryset = EducationalModule.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EducationalModuleFilter
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title', 'created_at']
    ordering = ['order']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'retrieve':
            return EducationalModuleDetailSerializer
        return EducationalModuleSerializer

    def perform_create(self, serializer):
        """Дополнительные действия при создании модуля"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Кастомное действие для активации/деактивации модуля"""
        module = self.get_object()
        module.is_active = not module.is_active
        module.save()
        return Response({'status': 'activated' if module.is_active else 'deactivated'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по модулям"""
        stats = {
            'total': self.get_queryset().count(),
            'active': self.get_queryset().filter(is_active=True).count(),
            'drafts': self.get_queryset().filter(status='DF').count(),
        }
        return Response(stats)

    def destroy(self, request, *args, **kwargs):
        """Кастомное удаление с проверками"""
        instance = self.get_object()
        if instance.status == EducationalModule.ModuleStatus.PUBLISHED:
            return Response(
                {'error': 'Нельзя удалять опубликованные модули'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
