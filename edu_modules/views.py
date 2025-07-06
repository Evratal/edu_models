# flake8: noqa: E501
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes
)

from .models import EducationalModule
from .serializers import EducationalModuleSerializer, EducationalModuleDetailSerializer, \
    EducationalModuleListSerializer, EducationalModuleCreateUpdateSerializer
from .filters import EducationalModuleFilter


class IsAdminOrReadOnly(BasePermission):
    """Разрешение: редактирование только для админов, чтение для всех"""

    def has_permission(self, request, view):
        return (
                request.method in ('GET', 'HEAD', 'OPTIONS') or
                request.user and
                request.user.is_staff
        )


@extend_schema_view(
    list=extend_schema(
        summary="Список образовательных модулей",
        description="Получение списка всех образовательных модулей с возможностью фильтрации и сортировки.",
        parameters=[
            OpenApiParameter(
                name='status',
                description='Фильтр по статусу модуля',
                required=False,
                enum=['DF', 'PB', 'AR'],
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='search',
                description='Поиск по названию и описанию',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='ordering',
                description='Сортировка (order, title, -created_at)',
                required=False,
                type=OpenApiTypes.STR
            ),
        ],
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value={
                    "count": 3,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Основы Python",
                            "order": 1,
                            "status": "PB"
                        }
                    ]
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Детали модуля",
        description="Получение детальной информации о конкретном образовательном модуле.",
        responses={
            200: EducationalModuleDetailSerializer,
            404: OpenApiResponse(description="Модуль не найден")
        }
    ),
    create=extend_schema(
        summary="Создание модуля",
        description="Создание нового образовательного модуля. Требуются права администратора.",
        request=EducationalModuleSerializer,
        responses={
            201: EducationalModuleSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    ),
    update=extend_schema(
        summary="Обновление модуля",
        description="Полное обновление образовательного модуля. Требуются права администратора.",
        request=EducationalModuleSerializer,
        responses={
            200: EducationalModuleSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    ),
    partial_update=extend_schema(
        summary="Частичное обновление модуля",
        description="Частичное обновление образовательного модуля. Требуются права администратора.",
        request=EducationalModuleSerializer,
        responses={
            200: EducationalModuleSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    ),
    destroy=extend_schema(
        summary="Удаление модуля",
        description="Удаление образовательного модуля. Нельзя удалять опубликованные модули.",
        responses={
            204: OpenApiResponse(description="Модуль удален"),
            400: OpenApiResponse(description="Нельзя удалить опубликованный модуль"),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    )
)
class EducationalModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с образовательными модулями.

    Поддерживает все стандартные CRUD операции, а также дополнительные действия:
    - Активация/деактивация модуля
    - Получение статистики

    ### Права доступа:
    - Чтение: доступно всем
    - Создание/изменение: только администраторам
    """
    queryset = EducationalModule.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EducationalModuleFilter
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title', 'created_at']
    ordering = ['order']

    def get_serializer_class(self):
        if self.action == 'list':
            return EducationalModuleListSerializer
        elif self.action == 'retrieve':
            return EducationalModuleDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EducationalModuleCreateUpdateSerializer
        return EducationalModuleSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="Активация модуля",
        description="Активация или деактивация образовательного модуля.",
        methods=["POST"],
        responses={
            200: OpenApiResponse(
                description="Статус изменен",
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value={"status": "activated"}
                    )
                ]
            ),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    )
    @extend_schema(
        summary="Активация модуля",
        description="Активация или деактивация образовательного модуля.",
        methods=["POST"],
        responses={
            200: OpenApiResponse(
                description="Статус изменен",
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value={"status": "activated", "is_active": True}
                    )
                ]
            ),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    )
    @action(detail=True, methods=['post'], url_path='activate', url_name='activate')
    def activate(self, request, pk=None):
        module = self.get_object()
        module.is_active = not module.is_active
        module.save()
        return Response({
            'status': 'activated' if module.is_active else 'deactivated',
            'is_active': module.is_active
        })

