import os

os.environ.setdefault("DJANGO_SECRET_KEY", "local-dev-only-not-for-production")
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend")
os.environ.setdefault("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("WEB_ORIGIN", "http://localhost:3000")
if not os.environ.get("DATABASE_URL"):
    os.environ.setdefault("ALLOW_SQLITE_DEV", "true")

from .base import *  # noqa: E402,F403
