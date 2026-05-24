"""
Management command: create_default_admin

Creates a default superuser on first deploy using environment variables.
Safe to re-run — skips creation if the user already exists.

Environment variables (set in Railway dashboard):
  DJANGO_ADMIN_USERNAME  (default: admin)
  DJANGO_ADMIN_EMAIL     (default: admin@umojaexchange.com)
  DJANGO_ADMIN_PASSWORD  (default: Admin@1234! — CHANGE THIS)
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create a default admin superuser from environment variables (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
        email    = os.environ.get("DJANGO_ADMIN_EMAIL",    "admin@umojaexchange.com")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "Admin@1234!")

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠  Admin "{username}" already exists — skipping.')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role="admin",
            first_name="Umoja",
            last_name="Admin",
        )

        self.stdout.write(self.style.SUCCESS(
            f"\n"
            f"  ✅  Default admin created\n"
            f"  ───────────────────────────────\n"
            f"  Username : {username}\n"
            f"  Email    : {email}\n"
            f"  Password : {password}\n"
            f"  ───────────────────────────────\n"
            f"  ⚠  Change the password after first login!\n"
        ))
