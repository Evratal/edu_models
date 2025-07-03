import django_filters
from django.db.models import Q
from .models import EducationalModule
from django.utils.translation import gettext_lazy as _
from django.forms import DateInput  # Используем стандартный виджет Django


class EducationalModuleFilter(django_filters.FilterSet):
    # Простые числовые фильтры
    order = django_filters.NumberFilter(field_name='order')
    order_min = django_filters.NumberFilter(
        field_name='order',
        lookup_expr='gte',
        label=_('Минимальный порядковый номер')
    )
    order_max = django_filters.NumberFilter(
        field_name='order',
        lookup_expr='lte',
        label=_('Максимальный порядковый номер')
    )

    # Фильтр по диапазону длительности
    duration_hours__range = django_filters.NumericRangeFilter(
        field_name='duration_hours',
        label=_('Диапазон длительности (часы)')
    )

    # Текстовый поиск с несколькими полями
    search = django_filters.CharFilter(
        method='custom_search',
        label=_('Поиск по названию и описанию')
    )

    # Фильтр по статусу с выбором
    status = django_filters.MultipleChoiceFilter(
        choices=EducationalModule.ModuleStatus.choices,
        label=_('Статус модуля'),
        conjoined=True  # AND-логика для нескольких значений
    )

    # Фильтр по активности с булевым преобразованием
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label=_('Только активные'),
        widget=django_filters.widgets.BooleanWidget(
            attrs={'class': 'form-check-input'}
        )
    )

    # Фильтр по дате создания (исправленная версия)
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label=_('Создано после'),
        widget=DateInput(attrs={'type': 'date'})  # Используем стандартный DateInput
    )

    class Meta:
        model = EducationalModule
        fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'description': ['icontains'],
        }

    def custom_search(self, queryset, name, value):
        """Кастомный поиск по нескольким полям"""
        search_terms = value.split()
        queries = []

        for term in search_terms:
            queries.append(Q(title__icontains=term))
            queries.append(Q(description__icontains=term))

        combined_query = queries.pop()
        for query in queries:
            combined_query |= query

        return queryset.filter(combined_query).distinct()

    @property
    def qs(self):
        """Дополнительная обработка queryset"""
        queryset = super().qs

        # Исключаем архивные по умолчанию
        if not self.form.cleaned_data.get('status'):
            queryset = queryset.exclude(
                status=EducationalModule.ModuleStatus.ARCHIVED
            )

        return queryset.order_by('order')
