"""
Django management command to create an admin superuser from environment variables.

Reads SEED_ADMIN_USERNAME, SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD,
SEED_ADMIN_FIRST_NAME, SEED_ADMIN_LAST_NAME from environment.
Idempotent: does nothing if a superuser already exists.
Safe: never prints password, never overwrites existing user's password.
"""
import os
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Create a Django superuser from SEED_ADMIN_* environment variables. "
        "Idempotent: safe to run multiple times; does not overwrite existing users."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Check if admin would be created without actually creating it.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)

        username = os.environ.get("SEED_ADMIN_USERNAME")
        email = os.environ.get("SEED_ADMIN_EMAIL")
        password = os.environ.get("SEED_ADMIN_PASSWORD")
        first_name = os.environ.get("SEED_ADMIN_FIRST_NAME", "Admin")
        last_name = os.environ.get("SEED_ADMIN_LAST_NAME", "User")

        if not all([username, email, password]):
            missing = []
            if not username:
                missing.append("SEED_ADMIN_USERNAME")
            if not email:
                missing.append("SEED_ADMIN_EMAIL")
            if not password:
                missing.append("SEED_ADMIN_PASSWORD")
            raise CommandError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Set them to create the initial admin user."
            )

        existing_superuser = User.objects.filter(is_superuser=True).first()
        if existing_superuser:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser already exists: {existing_superuser.email} "
                    f"({existing_superuser.username}) — skipping creation."
                )
            )
            return

        existing_username = User.objects.filter(username=username).first()
        if existing_username:
            self.stdout.write(
                self.style.WARNING(
                    f"User with username '{username}' exists but is not a superuser. "
                    "Not promoting automatically. Skipping creation."
                )
            )
            return

        existing_email = User.objects.filter(email=email).first()
        if existing_email:
            self.stdout.write(
                self.style.WARNING(
                    f"User with email '{email}' exists but is not a superuser. "
                    "Not promoting automatically. Skipping creation."
                )
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    f"DRY RUN: Would create superuser: username={username}, email={email}"
                )
            )
            return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role="ADMIN",
                is_email_verified=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created superuser: {user.email} ({user.username})"
                )
            )
        except Exception as e:
            raise CommandError(f"Failed to create superuser: {e}")