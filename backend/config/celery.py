import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("umoja_exchange")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ─── Periodic Tasks ──────────────────────────────────────────────
app.conf.beat_schedule = {
    "send-daily-report": {
        "task": "apps.notifications.tasks.send_daily_report_task",
        "schedule": crontab(hour=23, minute=59),
    },
    "send-monthly-report": {
        "task": "apps.notifications.tasks.send_monthly_report_task",
        "schedule": crontab(day_of_month=1, hour=8, minute=0),
    },
}
