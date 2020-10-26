# Generated by Django 2.2.16 on 2020-10-19 21:45

import cloudinary_storage.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0003_auto_20201018_0303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_pic',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='geospatialhub/course_pic/'),
        ),
        migrations.CreateModel(
            name='Pdf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('pdf_file', models.FileField(blank=True, storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(), upload_to='geospatialhub/pdf/')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdfs', to='learning.Module')),
            ],
        ),
    ]