# Generated by Django 4.1.13 on 2024-09-08 02:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BatchRequest',
            fields=[
                ('batch_id', models.AutoField(primary_key=True, serialize=False)),
                ('timeframe_string', models.CharField(blank=True, max_length=50, null=True)),
                ('keyword', models.CharField(blank=True, max_length=50, null=True)),
                ('begin_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('kw_id', models.AutoField(primary_key=True, serialize=False)),
                ('keyword', models.CharField(max_length=255, unique=True)),
                ('difficulty', models.IntegerField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
                ('sub_reddit', models.CharField(blank=True, max_length=255, null=True)),
                ('interest', models.TextField(blank=True, null=True)),
                ('forum_check', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrendingBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('d4s_id', models.CharField(blank=True, max_length=255, null=True)),
                ('google_trends_url', models.CharField(default=None, max_length=255, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Trending',
            fields=[
                ('trend_id', models.AutoField(primary_key=True, serialize=False)),
                ('frequency', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trends.trendingbatch')),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trends.keyword')),
            ],
        ),
        migrations.CreateModel(
            name='RelatedKeyword',
            fields=[
                ('related_kw_id', models.AutoField(primary_key=True, serialize=False)),
                ('frequency', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_kw', to='trends.keyword')),
                ('related_keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_kw', to='trends.keyword')),
            ],
        ),
        migrations.CreateModel(
            name='RankingForumPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateField(auto_now_add=True)),
                ('rank', models.IntegerField()),
                ('url', models.CharField(max_length=255)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trends.keyword')),
            ],
        ),
        migrations.CreateModel(
            name='NicheKeyword',
            fields=[
                ('niche_kw_id', models.AutoField(primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('niche_keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='niche_keyword', to='trends.keyword')),
                ('niche_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='niche_name', to='trends.keyword')),
            ],
        ),
        migrations.CreateModel(
            name='BatchResult',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('frequency', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trends.batchrequest')),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trends.keyword')),
            ],
        ),
    ]
