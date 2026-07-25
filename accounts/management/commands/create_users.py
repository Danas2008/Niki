from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Profile

USERS = [
    {"username": "daniel", "display_name": "Daniel", "role": "daniel", "is_staff": True},
    {"username": "niki", "display_name": "Niki", "role": "niki", "is_staff": False},
]


class Command(BaseCommand):
    help = "Create the 2 users (daniel, niki) with profiles and unusable passwords. Idempotent."

    def handle(self, *args, **options):
        for entry in USERS:
            user, created = User.objects.get_or_create(
                username=entry["username"],
                defaults={"is_staff": entry["is_staff"], "is_superuser": entry["is_staff"]},
            )
            if created:
                user.set_unusable_password()
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {entry['username']}"))
            else:
                self.stdout.write(f"User already exists: {entry['username']}")

            Profile.objects.get_or_create(
                user=user,
                defaults={"display_name": entry["display_name"], "role": entry["role"]},
            )

        self.stdout.write(self.style.WARNING(
            "Set passwords with: python manage.py changepassword <username>"
        ))
