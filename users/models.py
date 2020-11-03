from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from learning.models import Course
from django_currentuser.db.models import CurrentUserField
from django_currentuser.middleware import get_current_authenticated_user

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

    def get_enrolled_for(self):
        course_list = Course.objects.filter(enrolled_for=self.pk)
        course_enrolled = []
        for course in course_list:
            course_enrolled.append({"id": course.id, "title": course.title})
        return course_enrolled

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

class Post(models.Model):
    text = models.CharField(max_length=200)
    posted_by = CurrentUserField(related_name='posted_by')
    pub_date = models.DateTimeField('Publication Date', auto_now=True)
    image = models.ImageField(upload_to='post-images', null=True)
    in_reply_to_post = models.IntegerField(null=True)

    def get_readable_date(self):
        return self.pub_date.strftime("%B %d, %Y")

    def get_post_belongs_to_authenticated_user(self):
        return self.posted_by.pk == get_current_authenticated_user().pk

    def get_user(self):
        user_dict = vars(self.posted_by)
        return {"id": user_dict["id"], "username": user_dict["username"]}

    def get_likes_count(self):
        return PostRate.objects.filter(liked=True, rated_post=self).count()

    def get_dislikes_count(self):
        return PostRate.objects.filter(liked=False, rated_post=self).count()

    def get_comments(self):
        return Post.objects.filter(in_reply_to_post=self.pk)

    def get_comments_count(self):
        return Post.objects.filter(in_reply_to_post=self.pk).count()

    def __str__(self):
        return str(self)

class PostRate(models.Model):
    liked = models.BooleanField(null=True)
    rated_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.rated_post)