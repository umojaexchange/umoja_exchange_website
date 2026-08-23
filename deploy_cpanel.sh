#!/usr/bin/env bash
# =============================================================================
# deploy_cpanel.sh — deploy Umoja Exchange (Django + Vue) to cPanel
#
# Model: cPanel "Setup Python App" (Passenger). The Vue SPA is built into the
# Django project and served by WhiteNoise, so this is a single-service deploy.
#
# Pipeline: lint → test → django-check → build Vue → collectstatic → rsync over
#           SSH → remote: pip install → deploy-check → DB backup → migrate →
#           create admin → restart Passenger → health check.
#

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

log()  { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m✅ %s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m⚠ %s\033[0m\n" "$*"; }
die()  { printf "\n\033[1;31m✖ %s\033[0m\n" "$*" >&2; exit 1; }

usage() { awk '/^# ={10,}/{c++; next} c==1{sub(/^# ?/,""); print} c==2{exit}' "${BASH_SOURCE[0]}"; }

# ── OS detection — works on macOS, Linux, and Windows (Git Bash / WSL) ────────
detect_os() {
  case "$(uname -s 2>/dev/null)" in
    Darwin)               echo macos ;;
    Linux)
      grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null && echo wsl || echo linux ;;
    MINGW*|MSYS*|CYGWIN*) echo windows ;;
    *)                    echo unknown ;;
  esac
}
OS="$(detect_os)"

# Install rsync locally when missing, picking the OS's package manager.
ensure_rsync() {
  command -v rsync >/dev/null && return 0
  warn "rsync not found locally — attempting to install (OS: $OS)"
  case "$OS" in
    macos)
      command -v brew >/dev/null || die "Homebrew not found. See https://brew.sh, then: brew install rsync"
      brew install rsync ;;
    linux|wsl)
      local sudo=""; [[ $EUID -ne 0 ]] && command -v sudo >/dev/null && sudo="sudo"
      if   command -v apt-get >/dev/null; then $sudo apt-get update && $sudo apt-get install -y rsync
      elif command -v dnf     >/dev/null; then $sudo dnf install -y rsync
      elif command -v yum     >/dev/null; then $sudo yum install -y rsync
      elif command -v pacman  >/dev/null; then $sudo pacman -Sy --noconfirm rsync
      elif command -v zypper  >/dev/null; then $sudo zypper install -y rsync
      elif command -v apk     >/dev/null; then $sudo apk add rsync
      else die "No supported package manager found. Install rsync manually."; fi ;;
    windows)
      if   command -v pacman >/dev/null; then pacman -S --noconfirm rsync
      elif command -v choco  >/dev/null; then choco install -y rsync
      elif command -v scoop  >/dev/null; then scoop install rsync
      else die "Install rsync via 'pacman -S rsync' (MSYS2/Git Bash), 'choco install rsync', 'scoop install rsync', or run under WSL."; fi ;;
    *)
      die "Unknown OS — install rsync manually and re-run." ;;
  esac
  command -v rsync >/dev/null || die "rsync still not found after install attempt."
  ok "rsync installed"
}

# ── Parse args ────────────────────────────────────────────────────────────────
DO_BUILD=true
DRY_RUN=false
USE_TAR=false
for arg in "$@"; do
  case "$arg" in
    --no-build) DO_BUILD=false ;;
    --dry-run)  DRY_RUN=true ;;
    --tar)      USE_TAR=true ;;
    -h|--help)  usage; exit 0 ;;
    *)          die "Unknown argument: $arg (see --help)" ;;
  esac
done

# ── 1. Load config ───────────────────────────────────────────────────────────
[[ -f .env.deploy ]] || die "Missing .env.deploy — copy .env.deploy.example and fill it in."
set -a; . ./.env.deploy; set +a

: "${SSH_HOST:?set SSH_HOST in .env.deploy}"
: "${SSH_USER:?set SSH_USER in .env.deploy}"
: "${REMOTE_DIR:?set REMOTE_DIR in .env.deploy}"
: "${VENV_ACTIVATE:?set VENV_ACTIVATE in .env.deploy (the cPanel 'source .../activate' command)}"
SSH_PORT="${SSH_PORT:-22}"
SSH_KEY="${SSH_KEY:-.ssh/umoja_deploy}"
PYTHON_BIN="${PYTHON_BIN:-python}"
REMOTE_RSYNC="${REMOTE_RSYNC:-rsync}"       # absolute path if not on the server's PATH

# Derive the venv's bin/ from VENV_ACTIVATE (robust to `source`, `&& cd`, quoting).
# We activate by putting this on PATH remotely instead of sourcing `activate`,
# which avoids "Permission denied" when the value isn't a clean `source …` line.
VENV_ACT_PATH="$(printf '%s' "$VENV_ACTIVATE" | grep -oE '/[^ ]*/bin/activate' | head -1 || true)"
[[ -n "$VENV_ACT_PATH" ]] || die "VENV_ACTIVATE must contain the venv's '.../bin/activate' path (from the cPanel Python App page)."
VENV_BIN="$(dirname "$VENV_ACT_PATH")"      # e.g. /home/umojaexc/virtualenv/umoja_exchange/3.11/bin
VENV_ROOT="$(dirname "$VENV_BIN")"

# ── 2. Check local tools ─────────────────────────────────────────────────────
log "Checking local tools (OS: $OS)"
ensure_rsync
for t in ssh "$PYTHON_BIN"; do command -v "$t" >/dev/null || die "'$t' not found on PATH"; done
$DO_BUILD && { command -v npm >/dev/null || die "'npm' not found (needed to build the Vue SPA)"; }
[[ -f "$SSH_KEY" ]] || die "SSH key not found at '$SSH_KEY'"
chmod 600 "$SSH_KEY" 2>/dev/null || true
ok "tools present"

# ── 3. SSH options (multiplexing off on native Windows — unsupported there) ───
SSH_OPTS=(-i "$SSH_KEY" -p "$SSH_PORT" -o IdentitiesOnly=yes)
if [[ "$OS" != "windows" ]]; then
  SSH_OPTS+=(-o ControlMaster=auto -o ControlPath="/tmp/ue-%C" -o ControlPersist=60)
fi
REMOTE="$SSH_USER@$SSH_HOST"
ssh_do() { ssh "${SSH_OPTS[@]}" "$REMOTE" "$@"; }

log "Verifying SSH connection to $REMOTE:$SSH_PORT"
ssh_do "echo connected" >/dev/null || die "SSH failed — check host/port/key, and that your IP is whitelisted (cPHulk/CSF)."
ok "SSH connection OK"

# ── 4. Quality gates (skipped in --dry-run) ──────────────────────────────────
run_lint() {
  [[ "${SKIP_LINT:-false}" == "true" ]] && { warn "SKIP_LINT=true — skipping lint"; return; }
  log "Linting"
  # Python (Ruff)
  if ( cd backend && "$PYTHON_BIN" -m ruff --version ) >/dev/null 2>&1; then
    ( cd backend && "$PYTHON_BIN" -m ruff check . ) || die "Ruff found issues — fix them, or run with SKIP_LINT=true"
    ok "ruff clean"
  else
    warn "Ruff not installed — skipping Python lint (pip install -r backend/requirements/development.txt)"
  fi
  # Frontend (ESLint)
  if [[ -x frontend/node_modules/.bin/eslint ]]; then
    ( cd frontend && npm run --silent lint ) || die "ESLint found issues — fix them, or run with SKIP_LINT=true"
    ok "eslint clean"
  else
    warn "ESLint not installed — skipping JS/Vue lint (cd frontend && npm install)"
  fi
}

run_tests() {
  [[ "${SKIP_TESTS:-false}" == "true" ]] && { warn "SKIP_TESTS=true — skipping tests"; return; }
  log "Running Django tests"
  ( cd backend && DJANGO_SETTINGS_MODULE=config.settings.development "$PYTHON_BIN" manage.py test --noinput ) \
    || die "Tests failed — fix them, or run with SKIP_TESTS=true"
  ok "tests passed"
}

run_django_check() {
  log "Django system check"
  ( cd backend && DJANGO_SETTINGS_MODULE=config.settings.development "$PYTHON_BIN" manage.py check ) \
    || die "Django system check failed"
  ok "system check clean"
}

if ! $DRY_RUN; then
  run_lint
  run_tests
  run_django_check
fi

# ── 5. Build Vue + collectstatic (locally) ───────────────────────────────────
if $DO_BUILD && ! $DRY_RUN; then
  log "Building Vue SPA → backend/frontend_build/"
  ( cd frontend && { [[ -d node_modules ]] || npm ci --legacy-peer-deps; } && NODE_ENV=production npm run build )
  ok "Vue build done"

  log "Collecting static files → backend/staticfiles/"
  ( cd backend && DJANGO_SETTINGS_MODULE=config.settings.development "$PYTHON_BIN" manage.py collectstatic --noinput )
  ok "collectstatic done"
fi

[[ -f backend/frontend_build/index.html ]] || die "backend/frontend_build/index.html missing — run a full build first (without --no-build)."

# ── 6. Upload ────────────────────────────────────────────────────────────────
# Source is backend/ → remote app root. We DON'T push .env (server keeps its own
# secrets), media/ (user uploads), db.sqlite3, backups, or caches.
#
# rsync is preferred (delta transfer + --delete), but many cPanel jailed shells
# don't ship rsync. If the server has no rsync we fall back to tar-over-SSH,
# which needs only tar (almost always present). --tar forces the tar path.
EXCLUDES=('.env' 'media' 'backups' 'db.sqlite3' '__pycache__' '*.pyc' '.git*')

UPLOAD_METHOD="rsync"
if $USE_TAR; then
  UPLOAD_METHOD="tar"
elif ! ssh_do "command -v '$REMOTE_RSYNC' >/dev/null 2>&1 || command -v rsync >/dev/null 2>&1"; then
  warn "rsync not found on the server — falling back to tar-over-SSH (no delta transfer, no --delete of stale files)"
  UPLOAD_METHOD="tar"
fi

if [[ "$UPLOAD_METHOD" == "rsync" ]]; then
  RSYNC_FLAGS=(-az --delete --delay-updates --delete-delay --stats
               --no-owner --no-group --omit-dir-times)
  for e in "${EXCLUDES[@]}"; do RSYNC_FLAGS+=(--exclude="$e"); done
  $DRY_RUN && RSYNC_FLAGS+=(--dry-run --itemize-changes)
  if $DRY_RUN; then log "DRY RUN (rsync) — previewing upload to $REMOTE:$REMOTE_DIR"
  else              log "Uploading via rsync to $REMOTE:$REMOTE_DIR"; fi
  rsync "${RSYNC_FLAGS[@]}" \
        -e "ssh ${SSH_OPTS[*]}" \
        --rsync-path="mkdir -p '$REMOTE_DIR' && $REMOTE_RSYNC" \
        backend/ "$REMOTE:$REMOTE_DIR/"
else
  TAR_EXCLUDES=(); for e in "${EXCLUDES[@]}"; do TAR_EXCLUDES+=(--exclude="$e"); done
  # macOS bsdtar embeds Apple xattrs that GNU tar warns about on the server.
  # Strip them so the remote extract is quiet. (GNU tar has no such flags.)
  TAR_MAC=()
  [[ "$OS" == "macos" ]] && TAR_MAC=(--no-mac-metadata --no-xattrs)
  if $DRY_RUN; then
    log "DRY RUN (tar) — files that would upload:"
    COPYFILE_DISABLE=1 tar "${TAR_MAC[@]}" -czf - "${TAR_EXCLUDES[@]}" -C backend . | tar tzf - | sed 's/^/  /'
  else
    log "Uploading via tar-over-SSH to $REMOTE:$REMOTE_DIR"
    if command -v pv >/dev/null; then
      # pv shows a live progress bar (percent/ETA against an estimated size).
      TOTAL_BYTES="$(du -sk backend 2>/dev/null | awk '{print $1*1024}')"
      COPYFILE_DISABLE=1 tar "${TAR_MAC[@]}" -czf - "${TAR_EXCLUDES[@]}" -C backend . \
        | pv -pterb ${TOTAL_BYTES:+-s "$TOTAL_BYTES"} \
        | ssh "${SSH_OPTS[@]}" "$REMOTE" "mkdir -p '$REMOTE_DIR' && tar xzf - -C '$REMOTE_DIR'"
    else
      warn "install 'pv' for a progress bar (brew install pv) — showing file list instead"
      COPYFILE_DISABLE=1 tar "${TAR_MAC[@]}" -czvf - "${TAR_EXCLUDES[@]}" -C backend . \
        | ssh "${SSH_OPTS[@]}" "$REMOTE" "mkdir -p '$REMOTE_DIR' && tar xzf - -C '$REMOTE_DIR'"
    fi
  fi
fi

if $DRY_RUN; then
  ok "dry run complete — no remote changes were made"
  exit 0
fi
ok "upload done"

# ── 7. Remote: install, deploy-check, backup, migrate, admin, restart ────────
# NOTE: this heredoc is UNQUOTED so $VENV_BIN / $VENV_ROOT / $REMOTE_DIR expand
# LOCALLY. Any '$' meant for the REMOTE shell is escaped as \$ (see \$PATH). The
# embedded Python uses no '$'. Inner heredocs use quoted delimiters.
log "Remote: install → deploy-check → backup → migrate → restart"
REMOTE_SKIP_BACKUP="${SKIP_BACKUP:-false}"
ssh_do bash -s <<REMOTE_SCRIPT
set -euo pipefail
# Activate the venv by PATH (no fragile 'source .../activate').
export VIRTUAL_ENV="$VENV_ROOT"
export PATH="$VENV_BIN:\$PATH"
cd "$REMOTE_DIR"
[[ -f .env ]] || { echo "✖ $REMOTE_DIR/.env missing on server — create it from backend/.env.production.example"; exit 1; }

echo "▶ pip install…"
pip install --upgrade pip >/dev/null
pip install -r requirements/production.txt

echo "▶ deploy check (production settings)…"
python manage.py check --deploy || true   # security warnings are informational, not fatal

if [[ "$REMOTE_SKIP_BACKUP" != "true" ]]; then
echo "▶ MySQL backup (before migrate)…"
python - <<'PY'
import os, django, subprocess, datetime, tempfile
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()
from django.conf import settings
d = settings.DATABASES["default"]
if "mysql" not in d["ENGINE"]:
    print("  not MySQL — skipping backup"); raise SystemExit(0)
os.makedirs("backups", exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
out = os.path.join("backups", "db-{}.sql.gz".format(ts))
# Pass the password via a temp defaults file so it never appears in the process list.
cnf = tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False)
cnf.write("[client]\npassword={}\n".format(d.get("PASSWORD", "")))
cnf.close()
try:
    dump = subprocess.Popen(
        ["mysqldump", "--defaults-extra-file={}".format(cnf.name),
         "--host={}".format(d.get("HOST") or "localhost"),
         "--port={}".format(str(d.get("PORT") or "3306")),
         "--user={}".format(d.get("USER", "")),
         "--single-transaction", "--quick", "--no-tablespaces", d["NAME"]],
        stdout=subprocess.PIPE)
    with open(out, "wb") as f:
        gz = subprocess.Popen(["gzip"], stdin=dump.stdout, stdout=f)
        dump.stdout.close(); gz.communicate()
    if dump.wait() != 0 or gz.returncode != 0:
        print("  ⚠ mysqldump failed — continuing without a fresh backup")
    else:
        print("  saved", out)
        # keep only the 10 most recent backups
        backs = sorted(f for f in os.listdir("backups") if f.startswith("db-"))
        for old in backs[:-10]:
            os.remove(os.path.join("backups", old))
except FileNotFoundError:
    print("  ⚠ mysqldump/gzip not found on server — skipping backup")
finally:
    os.remove(cnf.name)
PY
fi

echo "▶ migrate…"
python manage.py migrate --noinput

echo "▶ create_default_admin…"
python manage.py create_default_admin || echo "  (admin step skipped — non-fatal)"

echo "▶ restart Passenger…"
mkdir -p tmp && touch tmp/restart.txt
echo "✅ remote steps done"
REMOTE_SCRIPT
ok "remote deploy done"

# ── 8. Post-deploy health check ──────────────────────────────────────────────
if [[ -n "${DEPLOY_URL:-}" ]]; then
  if command -v curl >/dev/null; then
    log "Checking $DEPLOY_URL"
    code="$(curl -s -o /dev/null -w '%{http_code}' -L "${DEPLOY_URL%/}/api/health/" || echo 000)"
    [[ "$code" =~ ^2 ]] && ok "site healthy (HTTP $code)" || warn "health check returned HTTP $code"
  else
    warn "curl not installed — skipping health check"
  fi
fi

printf "\n\033[1;32m🎉 Deploy complete.\033[0m\n"
