#!/usr/bin/env python
"""
One-shot server setup for cPanel's "Setup Python App → Execute python script".

Enter this in that field (relative to the Application root):

    server_setup.py

It runs, in order, against PRODUCTION settings + your server .env:
  1. migrate          — apply DB migrations to MySQL
  2. collectstatic    — gather the (already-uploaded) Vue build into staticfiles/
  3. create_default_admin — create the admin user if missing
  4. touch tmp/restart.txt — reload Passenger so changes take effect

It does NOT build the Vue SPA — that needs Node/npm and is done locally by
deploy_cpanel.sh, which uploads backend/frontend_build/ + staticfiles/ here.
So run a deploy (or upload the build) first; this script just wires up the DB
and static files and restarts the app.

Safe to re-run: migrate and create_default_admin are idempotent.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)                       # so .env + relative paths resolve
sys.path.insert(0, str(BASE_DIR))

# Force production settings regardless of how the script is invoked.
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production"

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402


def main():
    django.setup()

    print("▶ migrate…")
    call_command("migrate", "--noinput")

    print("▶ collectstatic…")
    call_command("collectstatic", "--noinput")

    print("▶ create_default_admin…")
    call_command("create_default_admin")

    print("▶ restart Passenger…")
    tmp = BASE_DIR / "tmp"
    tmp.mkdir(exist_ok=True)
    (tmp / "restart.txt").touch()

    print("✅ server setup complete")


if __name__ == "__main__":
    main()
