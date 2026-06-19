# core/management/commands/create_production_superuser.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = "Creates or updates a superuser for production using environment variables."

    def handle(self, *args, **options):
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        username = os.getenv("ADMIN_USERNAME")

        if not email or not password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment variables."
                )
            )
            return

        if not username:
            username = email.split("@")[0]

        try:
            user = User.objects.get(email=email)
            # Если пользователь уже есть — обновляем флаги и пароль
            updated = False
            if not user.is_superuser:
                user.is_superuser = True
                updated = True
            if not user.is_staff:
                user.is_staff = True
                updated = True
            if not user.username:
                user.username = username
                updated = True

            if updated:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Updated existing user to superuser: {email}")
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f"Superuser already exists and up to date: {email}")
                )

        except User.DoesNotExist:
            User.objects.create_superuser(
                email=email, username=username, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created superuser: {email}")
            )
