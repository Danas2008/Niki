from django.core.management.base import BaseCommand
from django.utils import timezone

from journey.models import Chapter

CHAPTERS = [
    {
        "key": "birthday",
        "title": "Všechno nejlepší, Niki",
        "teaser": "Něco tu na tebe čeká...",
        "unlock_at": (2026, 7, 27, 0, 0),
        "order": 1,
    },
    {
        "key": "departure",
        "title": "Cesta začíná",
        "teaser": "Nová kapitola začíná v den, kdy odletím...",
        "unlock_at": (2026, 8, 15, 0, 0),
        "order": 2,
    },
    {
        "key": "anniversary",
        "title": "Jeden rok",
        "teaser": "Celý rok nás dvou. Něco tu na tebe čeká...",
        "unlock_at": (2026, 9, 27, 0, 0),
        "order": 3,
    },
    {
        "key": "return",
        "title": "Návrat domů",
        "teaser": "Konec čekání. Něco tu na tebe čeká...",
        "unlock_at": (2026, 12, 19, 10, 0),
        "order": 4,
    },
]


class Command(BaseCommand):
    help = "Seed the 4 journey Chapters. Idempotent (get_or_create by key)."

    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()
        created_count = 0
        for entry in CHAPTERS:
            unlock_at = timezone.make_aware(timezone.datetime(*entry["unlock_at"]), tz)
            chapter, created = Chapter.objects.get_or_create(
                key=entry["key"],
                defaults={
                    "title": entry["title"],
                    "teaser": entry["teaser"],
                    "unlock_at": unlock_at,
                    "order": entry["order"],
                    "is_locked_default": True,
                    "body": "",
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded chapters: {created_count} created, {len(CHAPTERS) - created_count} already existed."
        ))
