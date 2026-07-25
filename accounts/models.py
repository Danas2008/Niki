from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ("daniel", "Daniel"),
        ("niki", "Niki"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"

    @property
    def is_niki(self):
        return self.role == "niki"

    @property
    def is_daniel(self):
        return self.role == "daniel"


def _user_is_niki(self):
    try:
        return self.profile.is_niki
    except Profile.DoesNotExist:
        return False


def _user_is_daniel(self):
    try:
        return self.profile.is_daniel
    except Profile.DoesNotExist:
        return False


# Attach convenience properties directly to User so views/templates can do
# `request.user.is_niki` / `request.user.is_daniel` without touching .profile.
User.is_niki = property(_user_is_niki)
User.is_daniel = property(_user_is_daniel)
