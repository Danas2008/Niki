from datetime import date

from django.db import models
from django.utils import timezone


DEFAULT_UNLOCK_DATE = date(2026, 8, 15)


class Letter(models.Model):
    number = models.IntegerField(unique=True)
    available_at = models.DateTimeField()
    unlock_date = models.DateField(default=DEFAULT_UNLOCK_DATE)
    category = models.CharField(max_length=120, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    is_big = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    is_virtual = models.BooleanField(default=False)
    virtual_password = models.CharField(max_length=128, blank=True, default="")
    virtual_content = models.TextField(blank=True, default="")
    has_code = models.BooleanField(default=False)
    unlock_code = models.CharField(
        max_length=100, blank=True,
        help_text="Kód napsaný uvnitř fyzického dopisu. Zadá ho online, až dopis otevře.",
    )
    web_content = models.TextField(blank=True)
    challenge_content = models.TextField(
        blank=True,
        help_text="Online výzva/vzkaz, který se odemkne až po zadání správného kódu z dopisu.",
    )

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Letter #{self.number}"

    def is_available(self, on_date=None):
        on_date = on_date or timezone.localdate()
        if self.is_mandatory:
            return self.unlock_date == on_date
        return self.unlock_date <= on_date

    def availability_label(self, on_date=None):
        on_date = on_date or timezone.localdate()
        if self.is_mandatory:
            if self.unlock_date == on_date:
                return "Today's letter!"
            if self.unlock_date > on_date:
                return f"Available on {self.unlock_date:%d.%m.%Y}"
            return f"Was available on {self.unlock_date:%d.%m.%Y}"
        if self.unlock_date > on_date:
            return f"Available on {self.unlock_date:%d.%m.%Y}"
        return "Available"


class LetterState(models.Model):
    letter = models.OneToOneField(Letter, on_delete=models.CASCADE, related_name="state")
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)
    mood = models.CharField(max_length=50, blank=True)
    code_unlocked = models.BooleanField(default=False)
    code_unlocked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"State for Letter #{self.letter.number}"


class UnlockCode(models.Model):
    TARGET_CHOICES = [
        ("time_capsule", "Time Capsule"),
        ("map_pin", "Map Pin"),
        ("gallery_album", "Gallery Album"),
        ("chapter", "Chapter"),
        ("love_wall_theme", "Love Wall Theme"),
    ]

    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id = models.IntegerField(null=True, blank=True)
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({self.label})"
