from django.apps import AppConfig


class EduModulesConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edu_modules'

    # Русскоязычное название для админ-панели
    verbose_name = 'Образовательные модули'

    def ready(self):

        pass
