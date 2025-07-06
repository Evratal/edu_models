from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import EducationalModule


@admin.register(EducationalModule)
class EducationalModuleAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления образовательными модулями.

    ### Особенности:
    - Гибкая настройка отображения списка модулей
    - Расширенные возможности фильтрации и поиска
    - Группировка полей в форме редактирования
    - Кастомные методы для отображения данных
    - Экспорт данных в CSV
    """

    # Настройки отображения в списке
    list_display = (
        'id',
        'order',
        'title',
        'status_badge',
        'short_description',
        'created_at',
        'duration_info',
        'actions_column'
    )
    list_display_links = ('title',)
    list_editable = ('order',)
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('order',)
    date_hierarchy = 'created_at'
    save_on_top = True
    actions = ['export_as_csv']
    list_per_page = 25

    # Форма редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('order', 'title', 'description'),
            'description': _('Основные настройки образовательного модуля')
        }),
        (_('Статус и видимость'), {
            'fields': ('status', 'is_active'),
            'classes': ('wide',)
        }),
        (_('Дополнительные параметры'), {
            'fields': ('duration_hours',),
            'classes': ('collapse',)
        }),
    )

    # Кастомные поля для отображения
    def status_badge(self, obj):
        colors = {
            'DF': 'gray',  # Черновик
            'PB': 'green',  # Опубликован
            'AR': 'orange'  # Архив
        }
        return format_html(
            '<span style="color: white; background-color: {};'
            'padding: 3px 8px; border-radius: 10px;">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )

    status_badge.short_description = _('Статус')
    status_badge.admin_order_field = 'status'

    def short_description(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description

    short_description.short_description = _('Описание')

    def created_at(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at.short_description = _('Дата создания')
    created_at.admin_order_field = 'created_at'

    def duration_info(self, obj):
        return _('{} часов ({} дн.)').format(
            obj.duration_hours,
            (obj.duration_hours + 7) // 8
        )

    duration_info.short_description = _('Длительность')

    def actions_column(self, obj):
        return format_html(
            '<a href="{}" class="button">Просмотр на сайте</a>',
            reverse('module-detail', args=[obj.pk])
        )

    actions_column.short_description = _('Действия')
    actions_column.allow_tags = True

    # Кастомные действия
    @admin.action(description=_('Экспорт выбранных в CSV'))
    def export_as_csv(self, request, queryset):
        """
        Экспорт выбранных модулей в CSV файл.
        Формат: ID,Название,Статус,Дата создания
        """
        import csv
        from django.http import HttpResponse
        from io import StringIO

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['ID', 'Title', 'Status', 'Created At'])

        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.title,
                obj.get_status_display(),
                obj.created_at.strftime('%Y-%m-%d')
            ])

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=modules_export.csv'
        return response

    # Переопределение методов
    def get_readonly_fields(self, request, obj=None):
        """Делаем поле 'created_by' доступным только для чтения"""
        if obj:
            return ('created_by',)
        return ()

    def save_model(self, request, obj, form, change):
        """Автоматическое сохранение пользователя при создании"""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Оптимизация запросов
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
