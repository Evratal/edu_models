from django.contrib.auth.models import User
from django.db import models
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError



class EducationalModule(models.Model):
    """
    Модель образовательного модуля с полной типизацией и бизнес-логикой.

    Атрибуты:
        order (int): Порядковый номер модуля (1-1000)
        title (str): Название модуля (до 255 символов)
        description (str): Подробное описание модуля
        status (str): Статус модуля (черновик/опубликован/архив)
        duration_hours (int): Продолжительность в часах (0-500)

    Методы:
        clean(): Валидация модели перед сохранением
        get_absolute_url(): URL для просмотра модуля
        status_badge(): HTML-представление статуса
    """

    class ModuleStatus(models.TextChoices):
        """Статусы образовательного модуля"""
        DRAFT = 'DF', _('Черновик')
        PUBLISHED = 'PB', _('Опубликован')
        ARCHIVED = 'AR', _('Архивный')
        __empty__ = _('(Не указано)')

    # Числовые поля
    order = models.PositiveIntegerField(
        verbose_name=_('Порядковый номер'),
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(1000)
        ],
        default=0,
        help_text=_('Уникальный порядковый номер от 1 до 1000')
    )

    # Текстовые поля
    title = models.CharField(
        verbose_name=_('Название модуля'),
        max_length=255,
        unique=True,
        help_text=_('Полное название образовательного модуля')
    )

    description = models.TextField(
        verbose_name=_('Подробное описание'),
        blank=True,
        default='',
        help_text=_('Полное описание содержания модуля')
    )

    # Метаданные
    created_at = models.DateTimeField(
        verbose_name=_('Дата создания'),
        auto_now_add=True  # Автоматически устанавливается при создании
    )

    created_by = models.ForeignKey(
        User,
        verbose_name=_('Автор'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_modules',
        help_text=_('Пользователь, создавший этот модуль')
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Дата обновления'),
        auto_now=True,
        editable=False
    )

    # Флаги и статусы
    is_active = models.BooleanField(
        verbose_name=_('Активен'),
        default=True,
        help_text=_('Доступен ли модуль для использования')
    )

    status = models.CharField(
        verbose_name=_('Текущий статус'),
        max_length=2,
        choices=ModuleStatus.choices,
        default=ModuleStatus.DRAFT,
        help_text=_('Статус публикации модуля')
    )

    # Параметры обучения
    duration_hours = models.PositiveSmallIntegerField(
        verbose_name=_('Длительность (часы)'),
        default=0,
        validators=[validators.MaxValueValidator(500)],
        help_text=_('Общая продолжительность обучения в часах (макс. 500)')
    )

    class Meta:
        verbose_name = _('Образовательный модуль')
        verbose_name_plural = _('Образовательные модули')
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['order'],
                name='unique_module_order',
                violation_error_message=_('Порядковый номер должен быть уникальным')
            ),
            models.UniqueConstraint(
                fields=['title'],
                name='unique_module_title',
                violation_error_message=_('Модуль с таким названием уже существует')
            )
        ]

    def __str__(self) -> str:
        """Строковое представление для административного интерфейса"""
        return f'{self.order}. {self.title} ({self.get_status_display()})'

    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()

        if self.status == self.ModuleStatus.PUBLISHED and not self.is_active:
            raise ValidationError({
                'is_active': _('Опубликованный модуль не может быть неактивным')
            })

        if self.duration_hours > 0 and not self.description:
            raise ValidationError({
                'description': _('Для модуля с ненулевой длительностью требуется описание')
            })

    def get_absolute_url(self):
        """URL для просмотра модуля на сайте"""
        return reverse('module-detail', kwargs={'pk': self.pk})

    @property
    def short_description(self) -> str:
        """Сокращенное описание (первые 100 символов)"""
        return (self.description[:100] + '...') if len(self.description) > 100 else self.description

    @property
    def duration_days(self) -> int:
        """Рассчитывает длительность в 8-часовых рабочих днях"""
        return (self.duration_hours + 7) // 8

    def status_badge(self) -> str:
        """Визуальное представление статуса (HTML)"""
        status_colors = {
            self.ModuleStatus.DRAFT: 'gray',
            self.ModuleStatus.PUBLISHED: 'green',
            self.ModuleStatus.ARCHIVED: 'orange'
        }
        return format_html(
            '<span style="color:white; background-color:{color}; padding:2px 6px; border-radius:4px;">{text}</span>',
            color=status_colors.get(self.status, 'gray'),
            text=self.get_status_display()
        )

    status_badge.short_description = _('Статус')
    status_badge.allow_tags = True
