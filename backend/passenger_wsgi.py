"""Passenger entry point for cPanel's "Setup Python App".

Point the Python App's **Application root** at this `backend/` directory and set
the **Application startup file** to `passenger_wsgi.py`. cPanel/Passenger imports
`application` from here and serves it — no gunicorn process to keep alive.

Restart the app after a deploy with:  touch tmp/restart.txt  (deploy_cpanel.sh
does this for you), or the "Restart" button in the cPanel Python App UI.
"""
import os
import sys

# Make `config`, `apps`, etc. importable regardless of Passenger's cwd.
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
