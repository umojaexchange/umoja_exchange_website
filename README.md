# Umoja Exchange 🟡

> Production-grade USDT/TZS crypto exchange management platform.
> **Django REST Framework** powers the API. **Vue 3** is the SPA frontend.
> Both run from a **single Django process** — one deploy, one domain, no CORS in production.

![Django](https://img.shields.io/badge/Backend-Django%205-green?style=flat-square)
![Vue](https://img.shields.io/badge/Frontend-Vue%203-brightgreen?style=flat-square)
![Deploy](https://img.shields.io/badge/Deploy-cPanel%20%28SSH%20%2B%20MySQL%29-orange?style=flat-square)

---

## How the Monorepo Works

```
Browser request to https://umojaexchange.co.tz/
│
├─ /api/v1/**        → Django REST Framework  (JSON)
├─ /admin/**         → Django admin panel
├─ /static/**        → WhiteNoise serves Vite build assets (JS, CSS)
└─ /**  (anything else) → Django returns Vue's index.html
                             └─ Vue Router takes over client-side
```

**Deploy pipeline (cPanel — see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)):**
```
npm run build          # Vue → backend/frontend_build/          (local)
collectstatic          # frontend_build/ → backend/staticfiles/ (local)
rsync over SSH         # backend/ → cPanel Application root
migrate                # Apply DB migrations on the server (MySQL)
touch tmp/restart.txt  # Passenger reloads — one app serves everything
```

**Local development (two terminals):**
```
Terminal 1:  cd backend && python manage.py runserver   # Django on :8000
Terminal 2:  cd frontend && npm run dev                  # Vite on :5173 (proxies /api → :8000)
```

---

## Quick Start

```bash
git clone https://github.com/your-org/umoja-exchange.git
cd umoja_exchange

# create virtual environment
python3 -m venv venv

# activate virtual environment
# macOS / Linux
source venv/bin/activate

# Windows CMD
venv\Scripts\activate

# 1. Install everything
cd backend && pip install -r requirements/development.txt && cd ..
cd frontend && npm install && cd ..

# 2. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum

# 3. Apply migrations
cd backend && python manage.py migrate

# 4. Create admin user
cd backend && python manage.py createsuperuser

# 5. Run both frontend and backend at once
sh dev.sh --seed  # → http://localhost:8000  & # Terminal 2 → http://localhost:5173

# Option A — Django only (build Vue first)
cd frontend && npm run build && cd ..
cd backend && python manage.py runserver     # → http://localhost:8000

# Option B — Hot-reload frontend (two terminals)
cd backend && python manage.py runserver     # Terminal 1 → http://localhost:8000
cd frontend && npm run dev                    # Terminal 2 → http://localhost:5173
```

> In **Option B** the Vite dev server (`localhost:5173`) proxies all `/api/`
> requests to Django at `localhost:8000`, so hot-reload works with live data.

---

## Project Structure

```
umoja_exchange/
├── backend/                     ← Django project root
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py          ← Shared; STATICFILES_DIRS → frontend_build/
│   │   │   ├── development.py   ← SQLite + DEBUG
│   │   │   └── production.py    ← MySQL + security headers
│   │   ├── urls.py              ← API routes + SPA catch-all
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── authentication/      ← Custom User model + JWT
│   │   ├── settings_app/        ← Singleton system settings
│   │   ├── purchases/           ← USDT purchases + InventoryLot
│   │   ├── sales/               ← FIFO engine + SaleLot audit trail
│   │   ├── dashboard/           ← KPI + chart data endpoints
│   │   ├── reports/             ← PDF (reportlab) + Excel (openpyxl)
│   │   ├── notifications/       ← Resend email + Celery tasks
│   │   └── audit_logs/          ← Full activity trail
│   ├── frontend_build/          ← ⚡ GENERATED — `npm run build` output
│   ├── staticfiles/             ← ⚡ GENERATED — `collectstatic` output
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt        ← + mysqlclient
│   ├── passenger_wsgi.py         ← cPanel "Setup Python App" entry point
│   ├── .env.production.example   ← Template for the server-side .env
│   └── manage.py
│
├── frontend/                    ← Vue 3 source
│   ├── src/
│   │   ├── api/                 ← Axios modules (relative /api/v1 base)
│   │   ├── router/              ← Vue Router + auth guards
│   │   ├── stores/              ← Pinia (auth, purchases, sales, dashboard)
│   │   ├── composables/         ← useToast
│   │   ├── layouts/             ← AppLayout (sidebar, dark mode)
│   │   ├── views/               ← LoginView, DashboardView, …
│   │   └── components/          ← Modal, ConfirmDialog, KpiCard, forms…
│   ├── vite.config.js           ← base: /static/, outDir: ../backend/frontend_build
│   └── package.json
│
├── docs/
│   └── DEPLOYMENT.md            ← Full cPanel deploy guide
├── deploy_cpanel.sh             ← Build + rsync + migrate + restart
├── .env.example                 ← Local dev env
├── .env.deploy.example          ← SSH/remote deploy config
└── README.md
```

---

## Environment Variables

Copy `.env.example` → `.env`:

| Variable | Required | Notes |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | ✅ | `config.settings.development` or `production` |
| `SECRET_KEY` | ✅ | 50+ random chars |
| `DEBUG` | ✅ | `True` dev, `False` prod |
| `ALLOWED_HOSTS` | ✅ | Comma-separated |
| `CSRF_TRUSTED_ORIGINS` | Prod | Comma-separated, with scheme (e.g. `https://umojaexchange.co.tz`) |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Prod | MySQL creds from cPanel (account-prefixed) |
| `DB_HOST` / `DB_PORT` | Prod | Default `localhost` / `3306` |
| `DATABASE_URL` | Optional | Overrides the `DB_*` vars if set (e.g. `mysql://…`) |
| `RESEND_API_KEY` | Optional | Automated email reports |
| `FROM_EMAIL` | Optional | Sender address |
| `REPORT_EMAIL` | Optional | Daily report recipient |
| `CORS_ALLOWED_ORIGINS` | Dev only | `http://localhost:5173` |

> Production runtime vars live in `<Application root>/.env` on the server — see
> [backend/.env.production.example](backend/.env.production.example). SSH/deploy
> settings live in your local `.env.deploy` — see [.env.deploy.example](.env.deploy.example).

The frontend has **no required env vars** in production — Axios uses the
relative `/api/v1` base URL since frontend and backend share the same origin.

---

## Deployment on cPanel (SSH + MySQL)

The app deploys to **cPanel** over **rsync/SSH**, running under **Passenger**
("Setup Python App") and backed by **MySQL**. The full walkthrough — SSH keys,
creating the MySQL database, the Python App, and the server `.env` — is in
**[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**. Short version:

### 1 — One-time setup

- Generate an SSH deploy key into `.ssh/` and authorize it in cPanel.
- Create the MySQL database + user (cPanel → MySQL Databases).
- Create the Python App (cPanel → Setup Python App): Application root =
  `umoja_exchange`, startup file = `passenger_wsgi.py`, entry point = `application`.
- On the server, create `<Application root>/.env` from
  [backend/.env.production.example](backend/.env.production.example).
- Locally, `cp .env.deploy.example .env.deploy` and fill in SSH details +
  the `VENV_ACTIVATE` command shown on the Python App page.

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2 — Deploy

```bash
./deploy_cpanel.sh             # build Vue + collectstatic (local) → rsync → migrate → restart
./deploy_cpanel.sh --no-build  # same, skipping the Vue rebuild
```

Under the hood ([deploy_cpanel.sh](deploy_cpanel.sh)): the SPA is
built and static collected **locally**, only finished files are rsynced (server
needs no Node), then remotely `pip install → migrate → create_default_admin →
touch tmp/restart.txt`.

### 3 — Admin user

The default admin is created automatically by `create_default_admin` from the
`DJANGO_ADMIN_*` vars in the server `.env`. To create one manually instead:
```bash
ssh -i .ssh/umoja_deploy -p <SSH_PORT> <SSH_USER>@<SSH_HOST>
source ~/virtualenv/umoja_exchange/3.11/bin/activate && cd ~/umoja_exchange
python manage.py createsuperuser
```

---

## API Reference

All endpoints prefixed with `/api/v1/` and require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login/` | Returns access + refresh tokens |
| POST | `/api/v1/auth/refresh/` | Refresh access token |
| POST | `/api/v1/auth/logout/` | Blacklist refresh token |
| GET | `/api/v1/auth/me/` | Current user |
| GET/POST | `/api/v1/purchases/` | List / create |
| GET/PUT/DELETE | `/api/v1/purchases/:id/` | Detail |
| GET | `/api/v1/purchases/inventory/` | Available USDT |
| GET | `/api/v1/sales/` | List |
| POST | `/api/v1/sales/create/` | FIFO sale |
| GET/DELETE | `/api/v1/sales/:id/` | Detail / delete + reverse |
| GET | `/api/v1/dashboard/summary/` | All KPIs |
| GET | `/api/v1/dashboard/charts/` | Chart datasets |
| GET | `/api/v1/reports/export/pdf/` | `?type=purchases\|sales&date_from=&date_to=` |
| GET | `/api/v1/reports/export/excel/` | Same params |
| GET/PUT | `/api/v1/settings/` | System settings |
| GET | `/api/health/` | Health check (no auth) |

---

## Running Celery (optional)

Celery uses the **DB as its broker** — no Redis required.

```bash
# Worker
cd backend && celery -A config worker --loglevel=info

# Beat (periodic tasks: daily report @ 23:59, monthly @ 1st 08:00)
cd backend && celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

On cPanel, run the worker and beat as **cron jobs** (or via the Python App's
"Execute python script" hook) against the app's virtualenv:
- Worker: `cd ~/umoja_exchange && celery -A config worker --loglevel=info`
- Beat: `cd ~/umoja_exchange && celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

> Note: shared cPanel hosting often restricts long-running processes — check with
> your host before relying on persistent Celery workers.

---

## FIFO Engine

`apps/sales/serializers.py → execute_fifo_sale()`

1. Locks `InventoryLot` rows oldest-first with `select_for_update()`
2. Validates available ≥ requested USDT
3. Consumes lots in order, tracking `(lot, amount)` pairs
4. Computes `avg_buy_rate = Σ(consumed × rate) / total`
5. Computes `profit_margin = sale_rate − avg_buy_rate`
6. Writes `Sale` + `SaleLot` records atomically in one transaction
7. Updates `InventoryLot.remaining` for each lot

Deletion reverses the FIFO via `reverse_fifo_sale()`.

---

## Command Reference

```bash
# Dependencies
cd backend && pip install -r requirements/development.txt   # Python deps
cd frontend && npm install                                  # Node deps

# Backend (run from backend/)
python manage.py migrate                                    # apply migrations (SQLite in dev)
python manage.py createsuperuser                            # create admin user
python manage.py runserver                                  # dev server :8000
python manage.py collectstatic --noinput                    # gather static files

# Lint (run before deploy; also gated inside deploy_cpanel.sh)
cd backend && ruff check . && cd ../frontend && npm run lint
cd backend && ruff check --fix .                            # auto-fix Python
cd frontend && npm run lint:fix                             # auto-fix JS/Vue

# Frontend (run from frontend/)
npm run dev                                                 # Vite dev server :5173 (hot reload)
npm run build                                               # compile Vue → backend/frontend_build/

# Celery (run from backend/)
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Deploy to cPanel (see docs/DEPLOYMENT.md)
./deploy_cpanel.sh                                          # build + rsync + migrate + restart
./deploy_cpanel.sh --no-build                              # deploy without rebuilding the SPA
```

---

## License

MIT © Umoja Exchange 2026
