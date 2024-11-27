from django.contrib import admin
from .models import Site, BlogPost, PinterestBoardSuggestion


class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created_on", "user")


class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "site", "title", "description", "url", "featured_image_url", "pin_image_url", "created_on", "date_modified")


class PinterestBoardSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        'blog_post',
        'board_name',
        'board_id',
        'match_score',
        'is_selected',
        'created_at'
    )
    list_filter = (
        'is_selected',
        'created_at'
    )
    search_fields = (
        'blog_post__title',
        'board_name'
    )
    readonly_fields = ('created_at',)


admin.site.register(Site, SiteAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(PinterestBoardSuggestion, PinterestBoardSuggestionAdmin)
