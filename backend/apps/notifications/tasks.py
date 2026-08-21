from celery import shared_task


@shared_task(name="apps.notifications.tasks.send_daily_report_task")
def send_daily_report_task():
    from .email import send_daily_report
    return send_daily_report()

@shared_task(name="apps.notifications.tasks.send_monthly_report_task")
def send_monthly_report_task():
    from .email import send_monthly_report
    return send_monthly_report()
