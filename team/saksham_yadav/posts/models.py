from django.conf import settings
from django.db import models
from django.db.models import Sum


class Post(models.Model):
    TEXT = "text"
    LINK = "link"
    IMAGE = "image"
    post_type = models.CharField(max_length=10, choices=[(TEXT, "Text"), (LINK, "Link"), (IMAGE, "Image")], default=TEXT)
    title = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    link_url = models.URLField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    community = models.ForeignKey("communities.Community", on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def score(self):
        return self.votes.aggregate(total=Sum("value"))["total"] or 0

    def __str__(self):
        return self.title


class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    image = models.ImageField(upload_to="post-media/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
