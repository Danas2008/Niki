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


class LandingSlide(models.Model):
    """One step of the post-login welcome sequence Niki sees before the
    dashboard. Slides with no title and no content are treated as not
    yet written and are skipped for non-builder viewers, but still show
    up (as blank placeholders) in builder mode so Dan can find and fill
    them in."""

    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Slide {self.order}"

    @property
    def is_written(self):
        return bool(self.title.strip() or self.content.strip())
