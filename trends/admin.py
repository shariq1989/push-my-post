from django.contrib import admin
from .models import BatchResult, BatchRequest, Trending, RelatedKeyword, Keyword, RankingForumPost, NicheKeyword, \
    TrendingBatch


class BatchResultAdmin(admin.ModelAdmin):
    list_display = ("result_id", "batch", "keyword", "frequency")


class BatchRequestAdmin(admin.ModelAdmin):
    list_display = ("keyword", "begin_date", "end_date")


class TrendingAdmin(admin.ModelAdmin):
    list_display = ("keyword", "frequency", "type", "batch")


class TrendingBatchAdmin(admin.ModelAdmin):
    list_display = ("d4s_id", "google_trends_url", "completed", "created_on")


class RelatedKeywordAdmin(admin.ModelAdmin):
    list_display = ("keyword", "related_keyword", "frequency", "type", "created_on")


class KeywordAdmin(admin.ModelAdmin):
    list_display = ("keyword", "difficulty", "volume", "updated_at", "interest", "forum_check")
    search_fields = ["keyword__icontains", "difficulty", "volume", "updated_at", "interest", "forum_check"]


class RankingForumPostAdmin(admin.ModelAdmin):
    list_display = ("keyword", "created_on", "rank", "url", "title")


class NicheKeywordsAdmin(admin.ModelAdmin):
    list_display = ('niche_kw_id', 'niche_name', 'niche_keyword', 'updated_at')


admin.site.register(BatchResult, BatchResultAdmin)
admin.site.register(BatchRequest, BatchRequestAdmin)
admin.site.register(Trending, TrendingAdmin)
admin.site.register(TrendingBatch, TrendingBatchAdmin)
admin.site.register(RelatedKeyword, RelatedKeywordAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(RankingForumPost, RankingForumPostAdmin)
admin.site.register(NicheKeyword, NicheKeywordsAdmin)
