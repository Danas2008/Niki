from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from jar.models import Letter

MANDATORY_NUMBERS = {1, 23, 44, 85, 127}
TOTAL_LETTERS = 127
START_DATE = date(2026, 8, 15)


def letter_category(number):
    if number == 1:
        return "Big one - departure"
    if number == 44:
        return "Anniversary"
    if number == 127:
        return "Big one - return"
    if number in MANDATORY_NUMBERS:
        return "Big one"
    if number == 9:
        return "Virtual"
    return "Free-choice"


class Command(BaseCommand):
    help = "Seed Letters #1-127. Idempotent and preserves custom content/passwords."

    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()
        created_count = 0

        for number in range(1, TOTAL_LETTERS + 1):
            unlock_date = START_DATE + timedelta(days=number - 1)
            available_at = timezone.make_aware(datetime.combine(unlock_date, time.min), tz)
            letter, created = Letter.objects.get_or_create(
                number=number,
                defaults={
                    "available_at": available_at,
                    "unlock_date": unlock_date,
                    "category": letter_category(number),
                    "is_big": number in MANDATORY_NUMBERS,
                    "is_mandatory": number in MANDATORY_NUMBERS,
                },
            )
            if created:
                created_count += 1

            letter.unlock_date = unlock_date
            letter.available_at = available_at
            letter.category = letter.category or letter_category(number)
            letter.is_big = letter.is_big or number in MANDATORY_NUMBERS
            letter.is_mandatory = number in MANDATORY_NUMBERS

            if number == 9:
                letter.is_virtual = True
                letter.has_code = True
                letter.unlock_code = letter.unlock_code or "N-98013"
                letter.notes = letter.notes or "Virtual letter. Password TBD in builder."

            letter.save()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded letters: {created_count} created, {TOTAL_LETTERS - created_count} already existed."
        ))
