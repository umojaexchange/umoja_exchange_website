#!/usr/bin/env bash
# =============================================================================
# scripts/start.sh — Railway RUNTIME start
# DB is reachable here — run migrations before gunicorn.
# =============================================================================
set -eo pipefail

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Umoja Exchange — Starting (port ${PORT:-8000})"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd backend

echo "▶ Running migrations..."
python manage.py migrate --run-syncdb
echo "✅  Migrations done"

echo "▶ Creating default admin if needed..."
python manage.py create_default_admin
echo "✅  Admin ready"

echo "▶ Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
