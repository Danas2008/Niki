from django.db import models


class MapPin(models.Model):
    KIND_CHOICES = [
        ("past", "Past"),
        ("present", "Present"),
        ("future", "Future"),
        ("milestone", "Milestone"),
    ]

    title = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    description = models.TextField(blank=True)
    unlock_at = models.DateTimeField(null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
