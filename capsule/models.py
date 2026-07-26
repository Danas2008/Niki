from django.conf import settings
from django.db import models

from jar.models import UnlockCode


class TimeCapsule(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    unlock_at = models.DateTimeField(null=True, blank=True)
    unlock_code = models.ForeignKey(
        UnlockCode, null=True, blank=True, on_delete=models.SET_NULL, related_name="time_capsules"
    )
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="time_capsules"
    )

    class Meta:
        ordering = ["unlock_at", "id"]

    def __str__(self):
        return self.title
