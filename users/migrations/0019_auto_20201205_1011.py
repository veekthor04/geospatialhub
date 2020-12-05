# Generated by Django 2.2.16 on 2020-12-05 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20201204_0017'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['-follower_count']},
        ),
        migrations.AddField(
            model_name='profile',
            name='banner_pic',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='geospatialhub/banner_pic/'),
        ),
    ]