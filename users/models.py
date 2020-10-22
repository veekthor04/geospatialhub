from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.IntegerField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='geospatialhub/profile_pic/', max_length=255, null=True, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location_city = models.CharField(max_length=50, blank=True)
    location_state = models.CharField(max_length=50, blank=True)
    location_country = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=50, blank=True)
    is_subscribed = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

