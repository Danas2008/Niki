from django.db import models


class MapPin(models.Model):
    KIND_CHOICES = [
        ("past", "Past"),
        ("present", "Present"),
        ("future", "Future"),
        ("milestone", "Milestone"),
    ]

    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    description = models.TextField(blank=True)
    unlock_at = models.DateTimeField(
        "Datum na cestě",
        null=True,
        blank=True,
        help_text="Určuje pořadí bodu na cestě a datum, které se u něj zobrazí. Celá cesta je vždy viditelná.",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
