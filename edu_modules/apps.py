from django.apps import AppConfig


class EduModulesConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edu_modules'  # Имя приложения (должно совпадать с именем папки приложения)

    # Русскоязычное название для админ-панели
    verbose_name = 'Образовательные модули'

    def ready(self):
        """
        Метод вызывается при готовности приложения.
        Здесь можно добавить сигналы или другие инициализации.
        """
        pass