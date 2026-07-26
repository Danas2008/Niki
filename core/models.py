from django.db import models


class TextBlock(models.Model):
    """A free-standing piece of page copy (e.g. the dashboard welcome
    message) that isn't naturally owned by any other model, but should
    still be editable inline via builder mode."""

    key = models.SlugField(unique=True)
    label = models.CharField(max_length=100, blank=True, help_text="Internal note, not shown on the site.")
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.label or self.key
