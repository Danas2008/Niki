from django.db import migrations


def seed_pins(apps, schema_editor):
    MapPin = apps.get_model("ourmap", "MapPin")

    MapPin.objects.get_or_create(
        title="Danovy narozeniny",
        kind="milestone",
        defaults={
            "lat": 0.0,
            "lng": 0.0,
            "description": "12. září 2026",
        },
    )
    MapPin.objects.get_or_create(
        title="Nikiny narozeniny",
        kind="milestone",
        defaults={
            "lat": 0.0,
            "lng": 0.0,
            "description": "27. července 2027",
        },
    )


def unseed_pins(apps, schema_editor):
    MapPin = apps.get_model("ourmap", "MapPin")
    MapPin.objects.filter(title__in=["Danovy narozeniny", "Nikiny narozeniny"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ourmap", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_pins, unseed_pins),
    ]
