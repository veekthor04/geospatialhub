# Generated by Django 2.2.16 on 2020-11-13 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_message_is_read'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='company',
            new_name='gender',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_subscribed',
        ),
        migrations.AddField(
            model_name='profile',
            name='institution',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='occupation',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='organisation',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]