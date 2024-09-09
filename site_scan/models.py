from django.db import models
from accounts.models import CustomUser


class Site(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    url = models.URLField()
    created_on = models.DateField(auto_now_add=True)
    last_scan = models.DateTimeField()

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
