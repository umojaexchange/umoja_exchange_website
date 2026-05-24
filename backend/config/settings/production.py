import dj_database_url
from .base import *  # noqa
from decouple import config

DEBUG = False

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Railway terminates SSL at the proxy — do NOT redirect here.
# If Django redirects the healthcheck (HTTP→HTTPS 301), Railway sees it as
# "service unavailable" and the deploy fails.
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS — only safe once SSL redirect is handled by the proxy, not Django
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Tell Django to trust Railway's X-Forwarded-Proto header so request.is_secure() works
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
