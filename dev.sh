#!/usr/bin/env bash
# =============================================================================
# dev.sh — run backend (Django :8000) + frontend (Vite :5173) together locally.
# Ctrl+C stops both. Uses SQLite dev settings (backend/.env → DB_ENGINE=sqlite).
#
#   ./dev.sh            # run both
#   ./dev.sh --seed     # (re)seed demo data first, then run
# =============================================================================
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

log() { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }

# Activate the local venv if present.
[[ -f .venv/bin/activate ]] && source .venv/bin/activate

# Dependency sanity.
command -v npm >/dev/null || { echo "npm not found"; exit 1; }
[[ -d frontend/node_modules ]] || { log "Installing frontend deps"; ( cd frontend && npm install ); }

# One-time DB prep.
log "Applying migrations (SQLite)"
( cd backend && python manage.py migrate --noinput )

if [[ "${1:-}" == "--seed" ]]; then
  log "Seeding demo data"
  ( cd backend && python manage.py seed_demo --clear )
fi

# Start both; kill the whole group on exit (Ctrl+C).
PIDS=()
cleanup() { log "Stopping…"; for p in "${PIDS[@]:-}"; do kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM

log "Backend  → http://localhost:8000"
( cd backend && python manage.py runserver ) &
PIDS+=("$!")

log "Frontend → http://localhost:5173  (open this one)"
( cd frontend && npm run dev ) &
PIDS+=("$!")

# Wait for either to exit, then cleanup runs via trap.
wait -n 2>/dev/null || wait
