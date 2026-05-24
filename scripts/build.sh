#!/usr/bin/env bash
# =============================================================================
# scripts/build.sh — Railway BUILD phase
# Runs inside the Docker image build — NO database access here.
# migrate + create_default_admin are in start.sh (runtime).
# =============================================================================
set -eo pipefail

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Umoja Exchange — Railway Build"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶ node $(node --version)  npm $(npm --version)  python $(python --version)"

# ── 1. Frontend ────────────────────────────────────────────────────
echo ""
echo "▶ [1/3] Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps
echo "✅  npm install done"

echo ""
echo "▶ [2/3] Building Vue 3 SPA..."
npm run build
echo "✅  Vite build done"
cd ..

# ── 2. Python deps ─────────────────────────────────────────────────
echo ""
echo "▶ [3/3] Installing Python dependencies..."
pip install --no-cache-dir --break-system-packages \
    -r backend/requirements/production.txt
echo "✅  pip install done"

# ── 3. collectstatic (no DB needed) ───────────────────────────────
echo ""
echo "▶ [+] Collecting static files..."
cd backend
python manage.py collectstatic --noinput
COUNT=$(find staticfiles -type f | wc -l)
echo "✅  $COUNT static files collected"
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Build complete (DB steps run at startup)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
