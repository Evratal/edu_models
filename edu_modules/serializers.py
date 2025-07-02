# flake8: noqa: E501
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import EducationalModule
from django.utils.translation import gettext_lazy as _


class EducationalModuleSerializer(serializers.ModelSerializer):
    """Основной сериализатор для образовательных модулей"""

    class Meta:
        model = EducationalModule
        fields = ['id', 'order', 'title', 'status', 'is_active', 'duration_hours']
        read_only_fields = ['id', 'status']

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError(_("Порядковый номер не может быть меньше 1"))
        return value


class EducationalModuleListSerializer(EducationalModuleSerializer):
    """Сериализатор для списка модулей"""
    short_description = serializers.SerializerMethodField()

    class Meta(EducationalModuleSerializer.Meta):
        fields = EducationalModuleSerializer.Meta.fields + ['short_description']

    def get_short_description(self, obj):
        return (obj.description[:100] + '...') if obj.description and len(obj.description) > 100 else obj.description


class EducationalModuleDetailSerializer(EducationalModuleSerializer):
    """Сериализатор для детального просмотра модуля"""
    duration_days = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta(EducationalModuleSerializer.Meta):
        fields = EducationalModuleSerializer.Meta.fields + [
            'description',
            'duration_days',
            'created_at',
            'updated_at'
        ]

    def get_duration_days(self, obj):
        return obj.duration_days


class EducationalModuleCreateUpdateSerializer(EducationalModuleSerializer):
    """Сериализатор для создания/обновления модулей"""

    class Meta(EducationalModuleSerializer.Meta):
        fields = EducationalModuleSerializer.Meta.fields + ['description']
        read_only_fields = ['id']

    def validate(self, data):
        if data.get('order', 0) > 100 and not self.context['request'].user.is_staff:
            raise serializers.ValidationError({
                'order': _("Только администраторы могут задавать порядок > 100")
            })
        return data
