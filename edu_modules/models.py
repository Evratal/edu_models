from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class EducationalModule(models.Model):
    """
    Модель образовательного модуля со строкой типизацией
    """

    class ModuleStatus(models.TextChoices):
        DRAFT = 'DF', _('Черновик')
        PUBLISHED = 'PB', _('Опубликован')
        ARCHIVED = 'AR', _('Архивный')

    # Числовые поля с валидацией
    order: int = models.PositiveIntegerField(
        verbose_name=_('Порядковый номер'),
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text=_('Число от 1 до 1000')
    )

    # Текстовые поля
    title: str = models.CharField(
        verbose_name=_('Название'),
        max_length=255,
        unique=True
    )

    description: str = models.TextField(
        verbose_name=_('Описание'),
        blank=True,
        default=''
    )

    # Дата/время
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name=_('Дата создания'),
        auto_now_add=True
    )

    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name=_('Дата обновления'),
        auto_now=True
    )

    # Логическое поле
    is_active: bool = models.BooleanField(
        verbose_name=_('Активен'),
        default=True
    )

    # Выбор из вариантов
    status: str = models.CharField(
        verbose_name=_('Статус'),
        max_length=2,
        choices=ModuleStatus.choices,
        default=ModuleStatus.DRAFT
    )

    # Целое число с ограничениями
    duration_hours: int = models.PositiveSmallIntegerField(
        verbose_name=_('Длительность (часы)'),
        default=0,
        validators=[MaxValueValidator(500)]
    )

    class Meta:
        verbose_name = _('Образовательный модуль')
        verbose_name_plural = _('Образовательные модули')
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['order'],
                name='unique_module_order'
            )
        ]

    def __str__(self) -> str:
        return f'{self.order}. {self.title}'

    @property
    def short_description(self) -> str:
        """Возвращает первые 100 символов описания"""
        return (self.description[:100] + '...') if len(self.description) > 100 else self.description

    @property
    def duration_days(self) -> int:
        """Рассчитывает длительность в 8-часовых рабочих днях"""
        return (self.duration_hours + 7) // 8