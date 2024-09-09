# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BatchRequest(models.Model):
    batch_id = models.AutoField(primary_key=True)
    timeframe_string = models.CharField(max_length=50, blank=True, null=True)
    keyword = models.CharField(max_length=50, blank=True, null=True)
    begin_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.batch_id} ({self.timeframe_string}, {self.keyword})"


class Keyword(models.Model):
    kw_id = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=255, unique=True)
    difficulty = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    volume = models.IntegerField(blank=True, null=True)
    sub_reddit = models.CharField(max_length=255, null=True, blank=True)
    interest = models.TextField(blank=True, null=True)
    forum_check = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.kw_id},{self.keyword}, {self.difficulty}, {self.volume}, {self.forum_check}"


class BatchResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(BatchRequest, on_delete=models.CASCADE)
    # cookies, biryani
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    frequency = models.IntegerField(blank=True, null=True)
    # related topic, rising query
    type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.keyword}"


class TrendingBatch(models.Model):
    d4s_id = models.CharField(max_length=255, blank=True, null=True)
    google_trends_url = models.CharField(max_length=255, null=True, default=None)
    completed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.d4s_id}, {self.completed}"


class Trending(models.Model):
    trend_id = models.AutoField(primary_key=True)
    # cookies, biryani
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    frequency = models.IntegerField(blank=True, null=True)
    # related topic, rising query
    type = models.CharField(max_length=255, blank=True, null=True)
    batch = models.ForeignKey(TrendingBatch, on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.trend_id}, {self.keyword},{self.frequency}, {self.type}, {self.created_on}, {self.batch}"


class RelatedKeyword(models.Model):
    related_kw_id = models.AutoField(primary_key=True)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='base_kw')
    related_keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='related_kw')
    frequency = models.IntegerField(blank=True, null=True)
    # related topic, rising query
    type = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.keyword} {self.related_keyword}"


class NicheKeyword(models.Model):
    niche_kw_id = models.AutoField(primary_key=True)
    niche_name = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='niche_name')
    niche_keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='niche_keyword')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.niche_name} {self.niche_keyword}"


class RankingForumPost(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    rank = models.IntegerField()
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.keyword}"
