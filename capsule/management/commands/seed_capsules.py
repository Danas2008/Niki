from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from capsule.models import TimeCapsule

CAPSULES = [
    {
        "title": "Naše první zpráva",
        "body": "Ahoj lásko, tohle je první kapsle času, kterou pro tebe otevírám. "
                "Chtěl jsem, abys hned na začátku měla něco hezkého na přečtení.",
        "unlock_offset_days": -3,  # already unlocked / in the past
    },
    {
        "title": "Dárek na později",
        "body": "Tahle kapsle se otevře, až přijde ten správný čas. Buď trpělivá, "
                "stojí to za to.",
        "unlock_offset_days": 14,  # locked, in the future
    },
    {
        "title": "Ještě jedno tajemství",
        "body": "Další malé překvapení, které si pro tebe schovávám na později.",
        "unlock_offset_days": 30,  # locked, further in the future
    },
]


class Command(BaseCommand):
    help = "Seed a few sample TimeCapsule rows (idempotent, keyed on title)."

    def handle(self, *args, **options):
        now = timezone.now()
        for entry in CAPSULES:
            unlock_at = now + timedelta(days=entry["unlock_offset_days"])
            obj, created = TimeCapsule.objects.get_or_create(
                title=entry["title"],
                defaults={
                    "body": entry["body"],
                    "unlock_at": unlock_at,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created capsule: {obj.title}"))
            else:
                self.stdout.write(f"Capsule already exists: {obj.title}")
