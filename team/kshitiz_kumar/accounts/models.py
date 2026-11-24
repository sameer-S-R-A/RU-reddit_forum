from django.conf import settings
from django.db import models
import uuid


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    bio = models.CharField(max_length=240, blank=True)
    avatar_url = models.URLField(blank=True)
    insforge_user_id = models.UUIDField(null=True, blank=True, unique=True, editable=False)

    def __str__(self):
        return f"{self.user.username}'s profile"
