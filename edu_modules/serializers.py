from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import EducationalModule


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример модуля',
            value={
                'id': 1,
                'order': 1,
                'title': 'Основы Python',
                'status': 'DF',
                'is_active': True,
                'duration_hours': 40
            },
            response_only=True
        )
    ]
)
class EducationalModuleSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для образовательных модулей.

    Поля:
    - id: Уникальный идентификатор (только чтение)
    - order: Порядковый номер (1-1000)
    - title: Название модуля
    - status: Статус модуля (DF/PB/AR)
    - is_active: Активен ли модуль
    - duration_hours: Длительность в часах
    """
    order = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message=_('Минимальное значение: 1')),
            MaxValueValidator(1000, message=_('Максимальное значение: 1000'))
        ],
        help_text=_('Порядковый номер модуля (от 1 до 1000)')
    )

    class Meta:
        model = EducationalModule
        fields = ['id', 'order', 'title', 'status', 'is_active', 'duration_hours']
        read_only_fields = ['id', 'status']
        extra_kwargs = {
            'title': {'help_text': _('Уникальное название модуля (до 255 символов)')},
            'status': {'help_text': _('Текущий статус модуля')},
            'is_active': {'help_text': _('Доступен ли модуль для использования')},
            'duration_hours': {'help_text': _('Продолжительность в часах (0-500)')},
        }

    def validate_order(self, value):
        """Проверка порядкового номера"""
        if value < 1:
            raise serializers.ValidationError(_("Порядковый номер не может быть меньше 1"))
        return value


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример списка модулей',
            value=[{
                'id': 1,
                'order': 1,
                'title': 'Основы Python',
                'status': 'DF',
                'is_active': True,
                'duration_hours': 40,
                'short_description': 'Введение в основы языка Python...'
            }],
            response_only=True
        )
    ]
)
class EducationalModuleListSerializer(EducationalModuleSerializer):
    """
    Сериализатор для списка модулей с кратким описанием.
    Добавляет поле short_description (первые 100 символов описания).
    """
    short_description = serializers.SerializerMethodField(
        help_text=_('Краткое описание (первые 100 символов)')
    )

    class Meta(EducationalModuleSerializer.Meta):
        fields = EducationalModuleSerializer.Meta.fields + ['short_description']

    def get_short_description(self, obj):
        return (obj.description[:100] + '...') if obj.description and len(obj.description) > 100 else obj.description


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример деталей модуля',
            value={
                'id': 1,
                'order': 1,
                'title': 'Основы Python',
                'status': 'DF',
                'is_active': True,
                'duration_hours': 40,
                'description': 'Полное описание модуля...',
                'duration_days': 5,
                'created_at': '2023-01-15 10:00',
                'updated_at': '2023-01-16 14:30'
            },
            response_only=True
        )
    ]
)
class EducationalModuleDetailSerializer(EducationalModuleSerializer):
    """
    Сериализатор для детального просмотра модуля.
    Добавляет:
    - Полное описание
    - Длительность в днях
    - Даты создания и обновления
    """
    duration_days = serializers.SerializerMethodField(
        help_text=_('Длительность в 8-часовых рабочих днях')
    )
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M',
        read_only=True,
        help_text=_('Дата и время создания')
    )
    updated_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M',
        read_only=True,
        help_text=_('Дата и время последнего обновления')
    )

    class Meta(EducationalModuleSerializer.Meta):
        fields = EducationalModuleSerializer.Meta.fields + [
            'description',
            'duration_days',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'description': {'help_text': _('Полное описание модуля')}
        }

    def get_duration_days(self, obj):
        return obj.duration_days


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Пример создания модуля',
            value={
                'order': 1,
                'title': 'Новый модуль',
                'description': 'Описание нового модуля',
                'duration_hours': 24,
                'is_active': True
            },
            request_only=True
        )
    ]
)
class EducationalModuleCreateUpdateSerializer(EducationalModuleSerializer):
    """
    Сериализатор для создания и обновления модулей.
    Добавляет поле description и расширенную валидацию.
    """
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=_('Полное описание модуля')
    )

    class Meta(EducationalModuleSerializer.Meta):
        fields = EducationalModuleSerializer.Meta.fields + ['description']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Проверка:
        - Только администраторы могут задавать order > 100
        - Опубликованные модули должны быть активными
        """
        if data.get('order', 0) > 100 and not self.context['request'].user.is_staff:
            raise serializers.ValidationError({
                'order': _("Только администраторы могут задавать порядок > 100")
            })

        if self.instance and self.instance.status == EducationalModule.ModuleStatus.PUBLISHED:
            if 'is_active' in data and not data['is_active']:
                raise serializers.ValidationError({
                    'is_active': _("Опубликованный модуль не может быть неактивным")
                })

        return data

    def validate_description(self, value):
        """Проверка описания для модулей с длительностью > 0"""
        if self.initial_data.get('duration_hours', 0) > 0 and not value:
            raise serializers.ValidationError(
                _("Для модуля с ненулевой длительностью требуется описание")
            )
        return value
