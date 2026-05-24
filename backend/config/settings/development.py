from .base import *  # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Allow Vite dev server during local development
CORS_ALLOW_ALL_ORIGINS = True

# In dev, WhiteNoise is still in MIDDLEWARE but STATICFILES_DIRS may be
# empty if frontend hasn't been built yet — that's fine, Vite serves assets.
