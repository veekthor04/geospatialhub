# Generated by Django 2.2.16 on 2020-10-18 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20201017_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_subscribed',
            field=models.BooleanField(default=False),
        ),
    ]
