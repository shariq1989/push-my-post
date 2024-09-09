from django.db import models
from django.conf import settings


class PinBoard(models.Model):
    board_id = models.IntegerField(null=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_on = models.DateField(auto_now_add=True)
    pin_count = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name}"


class PinterestPin(models.Model):
    pin_id = models.IntegerField(null=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_on = models.DateField(auto_now_add=True)
    pin_count = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)
    board_id = models.ForeignKey(PinBoard, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.keyword}"


class PinUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    board_count = models.IntegerField(null=True)
    pin_count = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    monthly_views = models.IntegerField(null=True)
    access_token = models.CharField(max_length=255, null=True)
    refresh_token = models.TextField(null=True)
    access_token_expiration_dt = models.DateTimeField(null=True)
    refresh_token_expiration_dt = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.name}"
