from django.contrib import admin
from .models import Site, BlogPost, PinterestBoardSuggestion


class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created_on", "user")


class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "site", "title", "description", "url", "featured_image_url", "pin_image_url", "created_on", "date_modified")


class PinterestBoardSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        'get_blog_post_title',
        'get_blog_post_description',
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
        'blog_post__title',  # Allows searching blog post titles
        'board_name'
    )
    readonly_fields = ('created_at',)

    @admin.display(ordering='blog_post__title', description='Blog Post Title')
    def get_blog_post_title(self, obj):
        return obj.blog_post.title

    @admin.display(ordering='blog_post__description', description='Blog Post Description')
    def get_blog_post_description(self, obj):
        return obj.blog_post.description


admin.site.register(Site, SiteAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(PinterestBoardSuggestion, PinterestBoardSuggestionAdmin)
