from .base import *  # noqa

DEBUG = True

# DATABASES comes from base.py (driven by DB_ENGINE / DATABASE_URL in .env).
# Locally that defaults to SQLite — no DB server needed.

# Allow Vite dev server during local development
CORS_ALLOW_ALL_ORIGINS = True

# In dev, WhiteNoise is still in MIDDLEWARE but STATICFILES_DIRS may be
# empty if frontend hasn't been built yet — that's fine, Vite serves assets.
