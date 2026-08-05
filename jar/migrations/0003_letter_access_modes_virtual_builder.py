import datetime

from django.db import migrations, models
from django.utils import timezone


MANDATORY_NUMBERS = {1, 23, 44, 85, 127}
TOTAL_LETTERS = 127
START_DATE = datetime.date(2026, 8, 15)


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


def seed_access_modes(apps, schema_editor):
    Letter = apps.get_model("jar", "Letter")
    tz = timezone.get_current_timezone()

    for number in range(1, TOTAL_LETTERS + 1):
        unlock_date = START_DATE + datetime.timedelta(days=number - 1)
        available_at = timezone.make_aware(
            datetime.datetime.combine(unlock_date, datetime.time.min),
            tz,
        )
        letter, _ = Letter.objects.get_or_create(
            number=number,
            defaults={
                "available_at": available_at,
                "unlock_date": unlock_date,
                "category": letter_category(number),
                "is_big": number in MANDATORY_NUMBERS,
                "is_mandatory": number in MANDATORY_NUMBERS,
            },
        )
        updates = {
            "unlock_date": unlock_date,
            "category": letter.category or letter_category(number),
            "is_big": letter.is_big or number in MANDATORY_NUMBERS,
            "is_mandatory": number in MANDATORY_NUMBERS,
        }
        if number == 9:
            updates.update({
                "is_virtual": True,
                "has_code": True,
                "unlock_code": letter.unlock_code or "N-98013",
                "notes": letter.notes or "Virtual letter. Password TBD in builder.",
            })
        Letter.objects.filter(pk=letter.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ("jar", "0002_letter_code_challenge"),
    ]

    operations = [
        migrations.AddField(
            model_name="letter",
            name="category",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="letter",
            name="is_mandatory",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="letter",
            name="is_virtual",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="letter",
            name="notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="letter",
            name="unlock_date",
            field=models.DateField(default=START_DATE),
        ),
        migrations.AddField(
            model_name="letter",
            name="virtual_content",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="letter",
            name="virtual_password",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.RunPython(seed_access_modes, migrations.RunPython.noop),
    ]
