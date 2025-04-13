from .settings import *

SECRET_KEY = "test-secret-key-unsafe-for-production"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop_profile",
    "my_app",
    "registration",
    "user_profile",
    "booking",  # Required for shop_profile/tests.py
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"