# Платформа для выкладывания платного контента - Django Project

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

## Быстрый старт

### Локальный запуск (без Docker)

# 1. Клонируйте репозиторий
```bash
git clone https://github.com/ваш-аккаунт/payment-platform.git
cd payment-platform
```

# 2. Создайте виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows
```

# 3. Установите зависимости
```bash
pip install -r requirements.txt
```

# 4. Создайте файл .env (скопируйте из примера)
```bash
cp .env.example .env
# Отредактируйте .env — добавьте свои Stripe ключи
```

# 5. Выполните миграции
```bash
python manage.py migrate
```

# 6. Создайте суперпользователя (администратора)
```bash
python manage.py createsuperuser
```

# 7. Запустите сервер
```bash
python manage.py runserver
```
