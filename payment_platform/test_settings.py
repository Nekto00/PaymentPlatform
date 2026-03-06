from .settings import *

# Используем SQLite для тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,  # Отключаем ATOMIC_REQUESTS для тестов
    }
}

# Отключаем debug toolbar для тестов
DEBUG = True
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Упрощаем пароли для тестов
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем логи
LOGGING_CONFIG = None

# Для тестов используем быстрый бэкенд
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Упрощаем статику
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# JWT для тестов
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': 'test-key',
}

# Stripe тестовые ключи
STRIPE_PUBLISHABLE_KEY = 'pk_test_test'
STRIPE_SECRET_KEY = 'sk_test_test'
STRIPE_WEBHOOK_SECRET = 'whsec_test'
STRIPE_PRICE_ID = 'price_test'
BASE_URL = 'http://testserver'