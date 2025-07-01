from django.contrib import admin
from .models import EducationalModule


@admin.register(EducationalModule)
class EducationalModuleAdmin(admin.ModelAdmin):
    # Настройки отображения в списке
    list_display = ('id', 'order', 'title', 'short_description', 'created_at')
    list_display_links = ('title',)  # Поля-ссылки на редактирование
    list_editable = ('order',)  # Поля, редактируемые прямо в списке
    list_filter = ('created_at',)  # Фильтры справа
    search_fields = ('title', 'description')  # Поля для поиска
    ordering = ('order',)  # Сортировка по умолчанию
    date_hierarchy = 'created_at'  # Иерархия по дате
    save_on_top = True  # Кнопки сохранения сверху

    # Форма редактирования
    fieldsets = (
        ('Основное', {
            'fields': ('order', 'title', 'description'),
            'description': 'Основные настройки модуля'
        }),
        ('Дополнительно', {
            'fields': ('is_active',),
            'classes': ('collapse',)  # Сворачиваемый блок
        }),
    )

    # Метод для сокращенного описания
    def short_description(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description

    short_description.short_description = 'Описание'

    # Метод для добавления в модель
    def created_at(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at.short_description = 'Создан'