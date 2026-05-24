#!/usr/bin/env bash
# =============================================================================
# scripts/build.sh — Railway build pipeline
# Called by: make railway-build  (via nixpacks.toml / railway.toml)
# =============================================================================
set -eo pipefail          # -e: exit on error  -o pipefail: catch pipe fails
                           # NOTE: no -u so missing env vars don't abort

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Umoja Exchange — Railway Build"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Sanity: confirm tools exist ────────────────────────────────────
echo "▶ node $(node --version)  npm $(npm --version)  python $(python --version)"

# ── 1. Frontend — install deps ─────────────────────────────────────
echo ""
echo "▶ [1/5] Installing frontend dependencies..."
cd frontend
# Use npm install (not ci) so a missing/stale lock-file doesn't abort
npm install --legacy-peer-deps
echo "✅  npm install done"

# ── 2. Frontend — Vite build ───────────────────────────────────────
echo ""
echo "▶ [2/5] Building Vue 3 SPA..."
npm run build
echo "✅  Vite build done"
cd ..

ls -lh backend/frontend_build/ | head -5

# ── 3. Python deps ─────────────────────────────────────────────────
echo ""
echo "▶ [3/5] Installing Python dependencies..."
pip install --no-cache-dir --break-system-packages -r backend/requirements/production.txt
echo "✅  pip install done"

# ── 4. collectstatic ───────────────────────────────────────────────
echo ""
echo "▶ [4/5] Collecting static files..."
cd backend
python manage.py collectstatic --noinput
COUNT=$(find staticfiles -type f | wc -l)
echo "✅  $COUNT static files collected"

# ── 5. Migrate + default admin ─────────────────────────────────────
echo ""
echo "▶ [5/5] Running migrations + creating default admin..."
python manage.py migrate --run-syncdb
python manage.py create_default_admin
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Build complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
