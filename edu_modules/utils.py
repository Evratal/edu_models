def get_module_stats():
    from .models import EducationalModule
    return {
        'total': EducationalModule.objects.count(),
        'active': EducationalModule.objects.filter(is_active=True).count()
    }