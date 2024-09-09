from django.contrib import admin
from .models import Site, BlogPost


class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created_on", "user")


class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
    "site", "title", "description", "url", "featured_image_url", "pin_image_url", "created_on", "date_modified")


admin.site.register(Site, SiteAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
