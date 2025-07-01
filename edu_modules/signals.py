from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import EducationalModule

@receiver(pre_save, sender=EducationalModule)
def update_module_order(sender, instance, **kwargs):
    if not instance.order:
        max_order = EducationalModule.objects.aggregate(models.Max('order'))['order__max'] or 0
        instance.order = max_order + 1