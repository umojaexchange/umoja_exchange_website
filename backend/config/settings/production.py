from .base import *  # noqa
from decouple import config, Csv

DEBUG = False

# Comma-separated list, e.g. "umojaexchange.co.tz,www.umojaexchange.co.tz"
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

# DATABASES comes from base.py (driven by DB_ENGINE / DATABASE_URL in .env).
# On the server set DB_ENGINE=mysql + DB_* (with DB_HOST=localhost).

# ── SECURITY ─────────────────────────────────────────────────────────────────
# Apache (with AutoSSL / Let's Encrypt) terminates TLS in front of Passenger and
# forwards X-Forwarded-Proto, so trust that header for request.is_secure().
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Redirect HTTP→HTTPS in Django. Turn OFF (SECURE_SSL_REDIRECT=False in .env)
# only if you haven't enabled SSL yet, otherwise the site becomes unreachable.
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Django 4+ requires the scheme in CSRF_TRUSTED_ORIGINS.
# e.g. "https://umojaexchange.co.tz,https://www.umojaexchange.co.tz"
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# HSTS — safe once SSL is live. Start small (e.g. 3600) if unsure, then raise.
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
