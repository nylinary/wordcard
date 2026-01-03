import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create an initial admin/superuser if it doesn't exist (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_ADMIN_USERNAME", "admin").strip().lower()
        email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@example.com").strip().lower()
        password = os.getenv("DJANGO_ADMIN_PASSWORD")
        first_name = os.getenv("DJANGO_ADMIN_FIRST_NAME", "Admin").strip()
        last_name = os.getenv("DJANGO_ADMIN_LAST_NAME", "User").strip()

        if not password:
            self.stdout.write(self.style.WARNING("DJANGO_ADMIN_PASSWORD is not set; skipping admin creation."))
            return

        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
            return

        changed = False
        # Ensure privileges
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True

        # Ensure required fields for your custom User model
        if not user.email:
            user.email = email
            changed = True
        if not user.first_name:
            user.first_name = first_name
            changed = True
        if not user.last_name:
            user.last_name = last_name
            changed = True

        if changed:
            user.save(
                update_fields=[
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "email",
                    "first_name",
                    "last_name",
                ]
            )
            self.stdout.write(self.style.SUCCESS(f"Updated existing user '{username}' to be admin."))
        else:
            self.stdout.write(f"Admin user '{username}' already exists.")
