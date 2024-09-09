from django.contrib import admin
from .models import PinUser


class PinUserAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "board_count", "pin_count", "follower_count", "following_count", "monthly_views",
                    "access_token", "refresh_token", "access_token_expiration_dt", "refresh_token_expiration_dt")


admin.site.register(PinUser, PinUserAdmin)
