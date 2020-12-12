# Generated by Django 2.2.16 on 2020-12-12 12:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_auto_20201212_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='enrolled_for',
            field=models.ManyToManyField(blank=True, related_name='enrolled_for', to=settings.AUTH_USER_MODEL),
        ),
    ]
