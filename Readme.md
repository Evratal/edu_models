# Educational Modules API



API для управления образовательными модулями с аутентификацией и CRUD-операциями.

## 🚀 Быстрый старт

### Предварительные требования
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.10+

### Запуск в development
```bash
git clone https://github.com/yourusername/edu_modules.git
cd edu_modules
```
# Сборка и запуск
docker-compose up -d --build

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
Доступные endpoints:

API: http://localhost:8000/api/modules/

Админка: http://localhost:8000/admin/

## 🛠 Технологический стек
Backend: Django 4.2 + DRF

База данных: PostgreSQL 14

Аутентификация: JWT

Инфраструктура: Docker + Docker Compose

## CI/CD: GitHub Actions

Production развертывание
1.Скопируйте .env.example в .env и настройте переменные

2.Запустите с production-настройками:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Настройка CI/CD
Автоматический деплой при пуше в ветку main:

1.Добавьте секреты в GitHub:

    SERVER_IP - IP сервера
    SSH_USER - пользователь SSH
    SSH_KEY - приватный ключ
    DEPLOY_DIR - путь на сервере (/home/user/edu_modules)

2.Workflow выполняет:

    Тестирование
    Деплой через Docker
    Миграции
    Сбор статики

📂 Структура проекта
edu_modules/
├── edu_modules/       # Основное приложение
├── config/            # Настройки Django
├── .github/workflows  # CI/CD скрипты
└── requirements       # Зависимости

## 🛡 Безопасность
Валидация паролей
Защита от CSRF
Лимиты запросов API
Автоматическое обновление зависимостей

## 🤝 Участие в разработке
Форкните репозиторий
Создайте feature-ветку (git checkout -b feature/AmazingFeature)
Зафиксируйте изменения (git commit -m 'Add some AmazingFeature')
Запушьте ветку (git push origin feature/AmazingFeature)
Откройте Pull Request
