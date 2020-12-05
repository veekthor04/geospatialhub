from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from learning.models import Course
from django_currentuser.db.models import CurrentUserField
from django_currentuser.middleware import get_current_user, get_current_authenticated_user
from datetime import date


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.IntegerField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='geospatialhub/profile_pic/', max_length=255, null=True, blank=True)
    banner_pic = models.ImageField(upload_to='geospatialhub/banner_pic/', max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location_city = models.CharField(max_length=50, blank=True)
    location_state = models.CharField(max_length=50, blank=True)
    location_country = models.CharField(max_length=50, blank=True)
    organisation = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    follower_count = models.PositiveSmallIntegerField(default=0)
    following_count = models.PositiveSmallIntegerField(default=0)

    def get_follow_status(self):
        follow_status = Follower.objects.filter(user = self.user, is_followed_by = get_current_authenticated_user())
        return "Following" if follow_status else "Follow"

    def get_unread_count(self):
        return  Message.objects.filter(receiver=self.user,is_read=False).count()

    def get_enrolled_for(self):
        course_list = Course.objects.filter(enrolled_for=self.pk)
        course_enrolled = []
        for course in course_list:
            course_enrolled.append({"id": course.id, "title": course.title})
        return course_enrolled

    def get_post_count(self):
        return  Post.objects.filter(posted_by=self.user).count()

    class Meta:
        ordering = ['-follower_count']

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
    image = models.ImageField(upload_to='geospatialhub/post-images/', null=True)
    in_reply_to_post = models.IntegerField(null=True)

    def get_post_belongs_to_authenticated_user(self):
        return self.posted_by.pk == get_current_authenticated_user().pk

    def get_authenticated_user_like_status(self):
        return PostRate.objects.filter(rated_by=get_current_authenticated_user(), rated_post= self, liked=True).exists()
    
    def get_user(self):
        return {"id": self.posted_by.id, "username": self.posted_by.username, 'first_name': self.posted_by.profile.first_name, 'last_name': self.posted_by.profile.last_name, 'profile_pic': self.posted_by.profile.profile_pic}

    def get_likes_count(self):
        return PostRate.objects.filter(liked=True, rated_post=self).count()

    def get_comments(self):
        return Post.objects.filter(in_reply_to_post=self.pk)

    def get_comments_count(self):
        return Post.objects.filter(in_reply_to_post=self.pk).count()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return str(self)

class PostRate(models.Model):
    liked = models.BooleanField(null=True)
    rated_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.rated_post)


class Follower(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    is_followed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='is_followed_by')
    is_viewed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def get_user_info(self):
        return {"id": self.user.id, "username": self.user.username, "first_name": self.user.profile.first_name, "last_name": self.user.profile.last_name,  "profile_pic": self.user.profile.profile_pic}

    def get_is_followed_by_info(self):
        return {"id": self.is_followed_by.id, "username": self.is_followed_by.username, "first_name": self.is_followed_by.profile.first_name, "last_name": self.is_followed_by.profile.last_name,  "profile_pic": self.is_followed_by.profile.profile_pic}
        
    def get_following(self, user):
        return Follower.objects.filter(is_followed_by=user)

    def get_followers(self, user):
        return Follower.objects.filter(user=user).exclude(is_followed_by=user)

    def get_following_count(self, user):
        return Follower.objects.filter(is_followed_by=user).count()

    def get_followers_count(self, user):
        return Follower.objects.filter(user=user).count()

    class Meta:
        ordering = ['-created']
        
    def __str__(self):
        return str(self)


class Message(models.Model):
    sender = CurrentUserField(related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    
    def get_sender(self):
        return {"id": self.sender.id, "username": self.sender.username}

    def get_receiver(self):
        return {"id": self.receiver.id, "username": self.receiver.username}

    def get_unread_count(self):
        return Message.objects.filter(receiver= get_current_authenticated_user(), is_read=False).count()
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.id