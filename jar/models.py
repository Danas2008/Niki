from django.db import models


class Letter(models.Model):
    number = models.IntegerField(unique=True)
    available_at = models.DateTimeField()
    is_big = models.BooleanField(default=False)
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
