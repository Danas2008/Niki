from django.db import models
from django.utils import timezone


class Chapter(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    teaser = models.CharField(max_length=300)
    unlock_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField()
    is_locked_default = models.BooleanField(default=True)
    body = models.TextField(blank=True)
    manually_unlocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

    def is_unlocked(self) -> bool:
        if self.manually_unlocked:
            return True
        if self.unlock_at is None:
            return not self.is_locked_default
        return self.unlock_at <= timezone.now()
