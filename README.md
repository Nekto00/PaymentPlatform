# Платформа для выкладывания плаьного контента - Django Project

Платформа для публикации платного контента с интеграцией Stripe и аутентификацией по номеру телефона.

## Особенности

- Регистрация пользователя по номеру телефона
- Аутентификация JWT для API
- Типы бесплатного и платного контента
- Интеграция платежей Stripe для подписок
- Адаптивный интерфейс на основе Bootstrap
- Контейнеризация Docker
- REST API с фреймворком Django REST
- База данных PostgreSQL

## Технический стек

- **Backend:** Django 6.0.2, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Payments:** Stripe API
- **Frontend:** Bootstrap 5, jQuery
- **Containerization:** Docker, Docker Compose
- **Testing:** Django TestCase, Coverage.py

## Установка

### Предварительные требования

- Docker and Docker Compose
- Python 3.13+
- PostgreSQL (если выполняется локально)
- Stripe account (для платежей)

### Настройка среды

1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/a_web_application_for_posting_paid_content.git
cd a_web_application_for_posting_paid_content
