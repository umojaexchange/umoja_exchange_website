# =============================================================================
# Umoja Exchange — Makefile
# =============================================================================

.PHONY: help install migrate superuser dev dev-frontend build \
        collectstatic celery-worker celery-beat clean \
        railway-build railway-start prod-local

SETTINGS_DEV  = config.settings.development
SETTINGS_PROD = config.settings.production

help:
	@printf "\n  \033[1;33mUmoja Exchange\033[0m\n"
	@printf "  ─────────────────────────────────────────────────────\n"
	@printf "  Local dev\n"
	@printf "    make install        Install Python + Node deps\n"
	@printf "    make migrate        Django migrate (SQLite)\n"
	@printf "    make superuser      Create superuser interactively\n"
	@printf "    make dev            Django runserver :8000\n"
	@printf "    make dev-frontend   Vite hot-reload :5173\n"
	@printf "    make build          Build Vue → backend/frontend_build/\n"
	@printf "    make collectstatic  Django collectstatic\n"
	@printf "    make prod-local     build + static + gunicorn :8000\n"
	@printf "  Celery\n"
	@printf "    make celery-worker  Start worker\n"
	@printf "    make celery-beat    Start beat scheduler\n"
	@printf "  Railway (used by railway.toml automatically)\n"
	@printf "    make railway-build  Full prod build pipeline\n"
	@printf "    make railway-start  Start Gunicorn\n"
	@printf "  Other\n"
	@printf "    make clean          Remove artefacts\n\n"

install:
	cd backend && pip install -r requirements/development.txt
	cd frontend && npm install

migrate:
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) python manage.py migrate

superuser:
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) python manage.py createsuperuser

dev:
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) python manage.py runserver

dev-frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build
	@echo "Vue built → backend/frontend_build/"

collectstatic:
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) python manage.py collectstatic --noinput

prod-local: build collectstatic
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_PROD) \
	    gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2

celery-worker:
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) celery -A config worker --loglevel=info

celery-beat:
	cd backend && DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) celery -A config beat --loglevel=info \
	    --scheduler django_celery_beat.schedulers:DatabaseScheduler

railway-build:
	bash scripts/build.sh

railway-start:
	bash scripts/start.sh

clean:
	rm -rf backend/frontend_build backend/staticfiles backend/db.sqlite3
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean done"
