from django.db import models
from accounts.models import CustomUser


class Site(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    url = models.URLField()
    created_on = models.DateField(auto_now_add=True)
    last_scan = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.name}"


class BlogPost(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    url = models.URLField()
    pin_image_url = models.URLField(null=True)
    featured_image_url = models.URLField()
    created_on = models.DateField(auto_now_add=True)
    date_modified = models.DateTimeField()

    def __str__(self):
        return f"{self.site}, {self.title}, {self.description}"


class PinterestBoardSuggestion(models.Model):
    """
    Stores individual board suggestions for a blog post
    """
    blog_post = models.ForeignKey(
        'BlogPost',
        on_delete=models.CASCADE,
        related_name='board_suggestions'
    )
    board_id = models.CharField(max_length=255)
    board_name = models.CharField(max_length=255)
    match_score = models.FloatField()
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog_post', 'board_id')
        ordering = ['-match_score']
