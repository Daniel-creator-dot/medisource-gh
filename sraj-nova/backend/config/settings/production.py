import os

os.environ["DJANGO_DEBUG"] = "false"

from .base import *  # noqa: E402,F403

DEBUG = False
if os.environ.get("MFA_REQUIRED_FOR_AGENCY_OWNER", "true").lower() in {"0", "false", "no"}:
    MFA_REQUIRED_FOR_AGENCY_OWNER = False
else:
    MFA_REQUIRED_FOR_AGENCY_OWNER = True

render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
