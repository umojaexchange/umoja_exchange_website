#!/usr/bin/env bash
# =============================================================================
# scripts/build.sh — Railway build script
# Called by railway.toml buildCommand = "make railway-build"
# =============================================================================
set -euo pipefail

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Umoja Exchange — Build"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Frontend ────────────────────────────────────────────────────
echo ""
echo "▶ [1/5] Installing frontend dependencies..."
cd frontend
npm ci --prefer-offline

echo ""
echo "▶ [2/5] Building Vue 3 → backend/frontend_build/ ..."
npm run build
cd ..

echo "✅  Frontend build complete"
ls -lh backend/frontend_build/

# ── 2. Backend Python deps ─────────────────────────────────────────
echo ""
echo "▶ [3/5] Installing Python dependencies..."
pip install -r backend/requirements/production.txt

# ── 3. Django collectstatic ────────────────────────────────────────
echo ""
echo "▶ [4/5] Collecting static files..."
cd backend
python manage.py collectstatic --noinput --settings=config.settings.production
echo "✅  Static files collected ($(find staticfiles -type f | wc -l) files)"

# ── 4. Migrate ─────────────────────────────────────────────────────
echo ""
echo "▶ [5/5] Running database migrations..."
python manage.py migrate --settings=config.settings.production

# ── 5. Default admin ───────────────────────────────────────────────
echo ""
echo "▶ [+] Creating default admin user if not exists..."
python manage.py create_default_admin --settings=config.settings.production
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Build finished successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
