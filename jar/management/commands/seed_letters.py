from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from jar.models import Letter

# Edit this list later with the specific letter numbers that should be
# flagged as "big" letters (5 total, TBD).
LETTER_BIG_NUMBERS = []

TOTAL_LETTERS = 127


class Command(BaseCommand):
    help = "Seed Letters #1-127. Idempotent (get_or_create by number)."

    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(
            timezone.datetime(2026, 8, 15, 0, 0, 0), tz
        )
        final_available_at = timezone.make_aware(
            timezone.datetime(2026, 12, 19, 10, 0, 0), tz
        )

        created_count = 0
        for number in range(1, TOTAL_LETTERS + 1):
            available_at = start + timedelta(days=number - 1)
            letter, created = Letter.objects.get_or_create(
                number=number,
                defaults={
                    "available_at": available_at,
                    "is_big": number in LETTER_BIG_NUMBERS,
                    "has_code": False,
                    "unlock_code": "",
                },
            )
            if created:
                created_count += 1

        # Letter #127's available_at must be exactly the return date/time.
        Letter.objects.filter(number=TOTAL_LETTERS).update(available_at=final_available_at)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded letters: {created_count} created, {TOTAL_LETTERS - created_count} already existed."
        ))
