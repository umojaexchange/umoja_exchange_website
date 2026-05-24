from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
]
LOCAL_APPS = [
    "apps.authentication",
    "apps.settings_app",
    "apps.purchases",
    "apps.sales",
    "apps.dashboard",
    "apps.reports",
    "apps.notifications",
    "apps.audit_logs",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.audit_logs.middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "config.urls"

# ── FRONTEND BUILD DIR ─────────────────────────────────────────────────────────
# `npm run build` writes Vite's output to backend/frontend_build/.
# Django template engine finds index.html there for the SPA catch-all view.
# collectstatic copies assets/ + favicon.svg etc. into STATIC_ROOT.
FRONTEND_BUILD_DIR = BASE_DIR / "frontend_build"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", FRONTEND_BUILD_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "authentication.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Dar_es_Salaam"
USE_I18N = True
USE_TZ = True

# ── STATIC FILES ───────────────────────────────────────────────────────────────
# WhiteNoise serves STATIC_ROOT at the /static/ URL prefix.
# We add the whole Vite build dir so collectstatic picks up:
#   frontend_build/assets/index-xxx.js  → /static/assets/index-xxx.js
#   frontend_build/favicon.svg          → /static/favicon.svg
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [FRONTEND_BUILD_DIR] if FRONTEND_BUILD_DIR.exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── REST FRAMEWORK ─────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# ── JWT ────────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ── CORS ───────────────────────────────────────────────────────────────────────
# Same-origin in production — only needed for local dev (Vite :5173 ↔ Django :8000)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ── CELERY (no Redis — django-db broker) ───────────────────────────────────────
CELERY_BROKER_URL = "django-db"
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ── EMAIL ──────────────────────────────────────────────────────────────────────
RESEND_API_KEY = config("RESEND_API_KEY", default="")
FROM_EMAIL = config("FROM_EMAIL", default="reports@umojaexchange.com")
REPORT_EMAIL = config("REPORT_EMAIL", default="")
