# Generated by Django 2.2.16 on 2020-12-03 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20201203_2349'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='follower',
            new_name='follower_count',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='following',
            new_name='following_count',
        ),
    ]