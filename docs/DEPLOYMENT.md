# Deployment Guide — Umoja Exchange (cPanel)

Django 5 API + Vue 3 SPA, deployed to **cPanel** over **rsync/SSH**, running under
**Passenger** ("Setup Python App"), backed by **MySQL**.

It's a **single service**: `npm run build` compiles the Vue SPA into
`backend/frontend_build/`, `collectstatic` gathers it into `backend/staticfiles/`,
and Django + WhiteNoise serve the whole app. There is no separate frontend host.

Deploys are driven from [`deploy_cpanel.sh`](../deploy_cpanel.sh):

```bash
./deploy_cpanel.sh             # build + rsync + migrate + restart
./deploy_cpanel.sh --no-build  # same, skipping the Vue rebuild
```

The build runs **on your machine**; only finished code + static files are rsynced,
so the server needs no Node. rsync sends only changed bytes, so re-deploys are fast.

Ad-hoc server commands (using the SSH details from `.env.deploy`):

```bash
# open a shell on the server
ssh -i .ssh/umoja_deploy -p <SSH_PORT> <SSH_USER>@<SSH_HOST>

# run migrations manually
ssh -i .ssh/umoja_deploy -p <PORT> <USER>@<HOST> \
  "source ~/virtualenv/umoja_exchange/3.11/bin/activate && cd ~/umoja_exchange && python manage.py migrate"

# restart the Passenger app
ssh -i .ssh/umoja_deploy -p <PORT> <USER>@<HOST> \
  "cd ~/umoja_exchange && mkdir -p tmp && touch tmp/restart.txt"
```

---

## One-time setup

### 1. SSH key

The key lives in the project at **`.ssh/umoja_deploy`** (private) +
**`.ssh/umoja_deploy.pub`** (public). `.ssh/` is gitignored — keys are never committed.

```bash
mkdir -p .ssh && chmod 700 .ssh
ssh-keygen -t ed25519 -f .ssh/umoja_deploy -N ""   # -N "" = no passphrase, so deploys never prompt
chmod 600 .ssh/umoja_deploy
```

- **Enable SSH**: cPanel → **SSH Access** (or **Terminal**). Note the **host** and
  **port** — cPanel often uses a non-standard port (e.g. `27522`, not 22).
- **Authorize the public key**: cPanel → SSH Access → **Manage SSH Keys → Import**,
  paste `.ssh/umoja_deploy.pub`, then **Manage → Authorize**.
- **Test**: `ssh -i .ssh/umoja_deploy -p <port> <cpaneluser>@<host>` — a clean login
  (no password prompt) means you're ready.

### 2. MySQL database

cPanel → **MySQL Databases**:

1. **Create a database** — e.g. `umoja`. cPanel prefixes it → `kitonga_umoja`.
2. **Create a user** — e.g. `umojauser` → `kitonga_umojauser`, with a strong password.
3. **Add the user to the database** with **ALL PRIVILEGES**.

Keep the final (prefixed) names and password — they go in the server `.env`.

### 3. cPanel Python App (Passenger)

cPanel → **Setup Python App** → **Create Application**:

| Field | Value |
| --- | --- |
| Python version | 3.11 (or the newest available) |
| Application root | `umoja_exchange` (creates `/home/<user>/umoja_exchange`) |
| Application URL | your domain / subdomain |
| Application startup file | `passenger_wsgi.py` |
| Application Entry point | `application` |

After it's created, copy the **"source .../activate"** command it displays — you'll
paste it verbatim into `.env.deploy` as `VENV_ACTIVATE`.

> **Application root** = your `REMOTE_DIR`. The deploy rsyncs the contents of the
> repo's `backend/` folder into it (so `passenger_wsgi.py`, `manage.py`, `config/`,
> and `.env` all sit at the app root).

### 4. Server `.env`

Create the runtime env file **on the server** (deploys never overwrite it):

```bash
ssh -i .ssh/umoja_deploy -p <SSH_PORT> <SSH_USER>@<SSH_HOST>
cd ~/umoja_exchange           # your REMOTE_DIR
nano .env                     # paste from backend/.env.production.example, fill in real values
```

Use [`backend/.env.production.example`](../backend/.env.production.example) as the
template — set `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and the
`DB_*` values from step 2.

### 5. Local `.env.deploy`

```bash
cp .env.deploy.example .env.deploy   # then edit
```

| Variable | Notes |
| --- | --- |
| `SSH_HOST` / `SSH_USER` / `SSH_PORT` | from cPanel → SSH Access |
| `SSH_KEY` | `.ssh/umoja_deploy` |
| `REMOTE_DIR` | the Python App's Application root, e.g. `/home/kitongalimited/umoja_exchange` |
| `VENV_ACTIVATE` | the exact `source .../activate` command from the Python App page |
| `PYTHON_BIN` | local python for `collectstatic` (your `.venv`); default `python` |
| `DEPLOY_URL` | optional — post-deploy check against `/api/health/` |

---

## Deploy

```bash
./deploy_cpanel.sh
```

What it does, in order ([`deploy_cpanel.sh`](../deploy_cpanel.sh)):

1. Loads `.env.deploy`, detects the OS, and checks/installs local tools
   (`ssh`, `rsync`, `npm`, `python`).
2. Opens a reused SSH connection (multiplexing off on native Windows) and verifies it.
3. **Quality gates** (abort on failure): Ruff lint → ESLint lint → `manage.py test`
   → `manage.py check`.
4. **Builds the Vue SPA** → `backend/frontend_build/`.
5. **collectstatic** (dev settings — no DB needed) → `backend/staticfiles/`.
6. **rsync** `backend/` → `REMOTE_DIR`, excluding `.env`, `media/`, `backups/`,
   `db.sqlite3`, and caches.
7. On the server: `pip install` → `manage.py check --deploy` (security posture) →
   **MySQL backup** (`backups/db-*.sql.gz`, keeps last 10) → `migrate` →
   `create_default_admin` → **restart Passenger** (`touch tmp/restart.txt`).
8. Health check against `DEPLOY_URL/api/health/` (skipped if `curl` is absent).

**Flags & toggles:**

```bash
./deploy_cpanel.sh --no-build   # skip the Vue rebuild + collectstatic
./deploy_cpanel.sh --dry-run    # preview the rsync file changes; make NO remote changes
./deploy_cpanel.sh --help

SKIP_LINT=true   ./deploy_cpanel.sh   # bypass the lint gate
SKIP_TESTS=true  ./deploy_cpanel.sh   # bypass the test gate
SKIP_BACKUP=true ./deploy_cpanel.sh   # skip the pre-migrate MySQL backup
```

> The lint gate needs the linters installed: Ruff via
> `pip install -r backend/requirements/development.txt`, ESLint via
> `cd frontend && npm install`. If a linter isn't installed the script **warns and
> skips** it rather than failing — so install them to make the gate real.

### Running the server-side steps from the cPanel UI

In production this is a **single Django app** — Django (WhiteNoise) serves the
built Vue SPA, so there is no separate frontend to run. Visiting the subdomain
serves both. cPanel's **Setup Python App → "Execute python script"** runs Python
only (it can't build the Vue SPA — that's done locally and uploaded), so it's for
the server-side setup steps.

Point it at [`server_setup.py`](../backend/server_setup.py) — enter this in the
field (path is relative to the Application root):

```
server_setup.py
```

It forces production settings and runs `migrate → collectstatic →
create_default_admin → touch tmp/restart.txt`. `deploy_cpanel.sh` already does all
of this automatically; `server_setup.py` is the manual equivalent for when you
deploy files another way (Git, File Manager) and want to finish setup from the UI.
Run a deploy / upload the build **first** — the script wires up the DB and static
files, it does not build the frontend.

You can also run individual steps in that same field, e.g.:

```
manage.py migrate
manage.py createsuperuser     # note: interactive prompts don't work in this field
```

---

## MySQL driver notes

Production uses `django.db.backends.mysql`. The driver is picked in
[`backend/config/__init__.py`](../backend/config/__init__.py):

- **`PyMySQL`** (the default in `requirements/production.txt`) is pure-Python, so it
  installs on jailed cPanel shells with **no compiler or MySQL dev headers**. The
  shim registers it as `MySQLdb` and spoofs `version_info` so it passes Django 5's
  "mysqlclient ≥ 1.4.3" check. This is what works on shared cPanel.
- **`mysqlclient`** is faster but needs a prebuilt manylinux wheel, or
  `libmysqlclient` + `gcc` + `pkg-config` to compile. Most jailed cPanel accounts
  lack these, so building it fails with *"Can not find valid pkg-config name"*. Only
  switch to it (comment PyMySQL, uncomment `mysqlclient` in `requirements/production.txt`)
  if your host provides those. The shim prefers `mysqlclient` automatically when it's
  importable.

---

## Troubleshooting

**`kex_exchange_identification: ... Not allowed at this time` / connection closed before login.**
The server firewall is refusing your IP *before* auth. Get your IP with `curl ifconfig.me`
and ask your host to whitelist it (WHM → cPHulk/CSF), or clear the temporary block.

**App won't start / 500 after deploy.**
Check the Passenger log shown in the cPanel Python App UI (or `tail -f stderr.log` in
the app root). Most common causes: missing/incorrect `.env` on the server, a `DB_*`
value wrong, or the domain not in `ALLOWED_HOSTS`.

**Static files (CSS/JS) 404.**
Confirm `collectstatic` ran (it's part of `./deploy_cpanel.sh`) and `staticfiles/`
rsynced. WhiteNoise serves `/static/` from it; the Vue build uses `base: '/static/'`.

**`DisallowedHost` / CSRF 403 on the admin.**
Add the domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (with `https://`) in the
server `.env`, then restart the app (`touch ~/umoja_exchange/tmp/restart.txt`).

**`rsync: command not found`.**
Two different cases:
- **Local** (your machine): the script auto-detects your OS (macOS / Linux / WSL /
  Windows Git Bash) and installs rsync via the right package manager (`brew`,
  `apt`/`dnf`/`yum`/`pacman`/`apk`, or `pacman`/`choco`/`scoop`). If auto-install
  can't run, it prints the exact command for your OS.
- **Remote** (`jailshell: rsync: command not found`): the server's jailed shell has
  no rsync. If rsync exists at a non-standard path, set `REMOTE_RSYNC=/full/path` in
  `.env.deploy` (find it with `ssh … "command -v rsync"`). **If the server has no
  rsync at all**, the script automatically falls back to **tar-over-SSH** (needs only
  tar, which the jail almost always has) — you'll see a "falling back to tar" warning
  and the deploy continues. Force it anytime with `./deploy_cpanel.sh --tar`.
  You can't install system rsync from a jailed shell (needs root); to get real rsync
  back, ask your host to install it and add it to CageFS for your account.

**Redirect loop / site unreachable right after enabling.**
SSL isn't active yet but `SECURE_SSL_REDIRECT=True`. Enable cPanel AutoSSL first, or
temporarily set `SECURE_SSL_REDIRECT=False` in the server `.env` and restart.

**Changes don't show up.**
Passenger caches the loaded app — restart it with `touch ~/umoja_exchange/tmp/restart.txt`.

---

## What is / isn't deployed

- **Pushed**: everything under `backend/` — `config/`, `apps/`, `manage.py`,
  `passenger_wsgi.py`, `requirements/`, the built `frontend_build/` and `staticfiles/`.
- **Never pushed**: the server `.env` (its own secrets), `media/` (user uploads),
  `db.sqlite3`, `__pycache__`, `.git`.

---

## Local development

```bash
cd backend && pip install -r requirements/development.txt   # Python deps
cd frontend && npm install                                  # Node deps

cd backend && python manage.py migrate                      # SQLite
cd backend && python manage.py runserver                    # Django :8000
cd frontend && npm run dev                                  # Vite hot-reload :5173
```
