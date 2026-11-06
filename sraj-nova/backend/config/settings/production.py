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

# The Render database already contains the earlier marketplace schema.
# Keep this application's tables in their own schema.
if "postgresql" in DATABASES["default"]["ENGINE"]:
    database_options = DATABASES["default"].setdefault("OPTIONS", {})
    database_options["options"] = "-c search_path=nova"

SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^api/v1/health/$"]
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
