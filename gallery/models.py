from django.db import models

from jar.models import UnlockCode


class GalleryPhoto(models.Model):
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=300, blank=True)
    taken_on = models.DateField(null=True, blank=True)
    album = models.CharField(max_length=100, blank=True)
    unlock_at = models.DateTimeField(null=True, blank=True)
    unlocked_by_code = models.ForeignKey(
        UnlockCode, null=True, blank=True, on_delete=models.SET_NULL, related_name="gallery_photos"
    )

    class Meta:
        ordering = ["album", "taken_on"]

    def __str__(self):
        return self.caption or f"Photo #{self.pk}"
