# Generated by Django 4.1.13 on 2024-09-10 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_scan', '0003_alter_site_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='created_on',
            field=models.DateField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='site',
            name='last_scan',
            field=models.DateTimeField(null=True),
        ),
    ]
