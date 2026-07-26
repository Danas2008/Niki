from django.db import migrations
from django.utils import timezone


def seed_path(apps, schema_editor):
    MapPin = apps.get_model("ourmap", "MapPin")
    tz = timezone.get_current_timezone()

    MapPin.objects.get_or_create(
        title="Poznali jsme se",
        kind="past",
        defaults={
            "lat": 0.0,
            "lng": 0.0,
            "description": "",
            "unlock_at": timezone.make_aware(timezone.datetime(2025, 7, 21, 0, 0), tz),
        },
    )
    MapPin.objects.get_or_create(
        title="Uvidíme se znovu",
        kind="future",
        defaults={
            "lat": 0.0,
            "lng": 0.0,
            "description": "",
            "unlock_at": timezone.make_aware(timezone.datetime(2026, 12, 19, 10, 0), tz),
        },
    )

    # The two birthday markers were seeded as always-visible date notes
    # (0002_seed_birthday_pins). Now that the timeline is a connected path
    # of points that unlock as time passes, give them real dates on that
    # path too instead of being permanently unlocked.
    MapPin.objects.filter(title="Danovy narozeniny").update(
        unlock_at=timezone.make_aware(timezone.datetime(2026, 9, 12, 0, 0), tz),
        description="",
    )
    MapPin.objects.filter(title="Nikiny narozeniny").update(
        unlock_at=timezone.make_aware(timezone.datetime(2027, 7, 27, 0, 0), tz),
        description="",
    )


def unseed_path(apps, schema_editor):
    MapPin = apps.get_model("ourmap", "MapPin")
    MapPin.objects.filter(title__in=["Poznali jsme se", "Uvidíme se znovu"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ourmap", "0002_seed_birthday_pins"),
    ]

    operations = [
        migrations.RunPython(seed_path, unseed_path),
    ]
