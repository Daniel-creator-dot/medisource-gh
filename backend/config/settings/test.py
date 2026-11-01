import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("ALLOW_SQLITE_DEV", "true")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "http://testserver,http://localhost:3000")

from .base import *  # noqa: E402,F403

DEBUG = True
MFA_REQUIRED_FOR_PRIVILEGED = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "medisource-tests",
    }
}

# A developer .env may point at PostgreSQL. The default test run stays on SQLite.
# Continuous integration sets USE_POSTGRES_TESTS=true together with DATABASE_URL.
if os.environ.get("USE_POSTGRES_TESTS") != "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "auth": "10000/minute",
        "anon": "10000/minute",
        "user": "10000/minute",
        "contact": "10000/hour",
    },
}
