from django.contrib.auth.models import User
from django.db import models


class LoveWallPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lovewall_posts")
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="lovewall/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author} at {self.created_at:%Y-%m-%d %H:%M}"
