# Generated by Django 2.2.16 on 2020-12-12 11:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(auto_now=True, verbose_name='Publication Date')),
                ('image', models.ImageField(null=True, upload_to='geospatialhub/post-images/')),
                ('in_reply_to_post', models.IntegerField(null=True)),
                ('posted_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posted_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('profile_pic', models.ImageField(blank=True, max_length=255, null=True, upload_to='geospatialhub/profile_pic/')),
                ('banner_pic', models.ImageField(blank=True, max_length=255, null=True, upload_to='geospatialhub/banner_pic/')),
                ('gender', models.CharField(blank=True, max_length=50)),
                ('bio', models.TextField(blank=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('location_city', models.CharField(blank=True, max_length=50)),
                ('location_state', models.CharField(blank=True, max_length=50)),
                ('location_country', models.CharField(blank=True, max_length=50)),
                ('organisation', models.CharField(blank=True, max_length=200)),
                ('occupation', models.CharField(blank=True, max_length=200)),
                ('institution', models.CharField(blank=True, max_length=200)),
                ('follower_count', models.PositiveSmallIntegerField(default=0)),
                ('following_count', models.PositiveSmallIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-follower_count'],
            },
        ),
        migrations.CreateModel(
            name='PostRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked', models.BooleanField(null=True)),
                ('rated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('rated_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_viewed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_followed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_followed_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
