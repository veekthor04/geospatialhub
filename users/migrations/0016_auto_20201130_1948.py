# Generated by Django 2.2.16 on 2020-11-30 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20201126_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(null=True, upload_to='geospatialhub/post-images/'),
        ),
    ]