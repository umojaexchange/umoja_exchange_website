# ── MySQL driver ─────────────────────────────────────────────────────────
# Prefer mysqlclient (the driver Django officially supports). If it isn't
# installed — e.g. it couldn't compile on cPanel shared hosting — fall back to
# PyMySQL, which is pure-Python and installs anywhere. install_as_MySQLdb()
# makes `django.db.backends.mysql` use PyMySQL under the MySQLdb name.
try:
    import MySQLdb  # noqa: F401  (mysqlclient — preferred)
except ImportError:
    try:
        import pymysql

        # Django 5's mysql backend requires "mysqlclient >= 1.4.3". PyMySQL reports
        # its own (lower) version, so spoof it to satisfy that check before setup.
        pymysql.version_info = (1, 4, 6, "final", 0)
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

from .celery import app as celery_app

__all__ = ("celery_app",)
