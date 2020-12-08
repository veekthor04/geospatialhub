from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django_currentuser.db.models import CurrentUserField
from django_currentuser.middleware import get_current_user, get_current_authenticated_user
import users.models

# Create your models here.
class Category(models.Model):

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        
        ordering = ['title']
        
    def __str__(self):
        
        return self.title

class Course(models.Model):

    author = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    course_pic = models.ImageField(upload_to='geospatialhub/course_pic/', max_length=255, null=True, blank=True)
    overview = models.TextField()
    estimated_time = models.PositiveSmallIntegerField(help_text="Should be in hours")
    price = models.PositiveIntegerField(default=0)
    price_before_discount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    enrolled_for = models.ManyToManyField(User, related_name='enrolled_for')
    
    class Meta:
    
        ordering = ['-created']

    def get_author(self):
        profile = users.models.Profile.objects.get(user=self.author)
        return {"id": profile.id, "first_name": profile.first_name, "last_name": profile.last_name}

    def get_category(self):
        return {"id": self.category.id, "title": self.category.title}

    def get_is_user_enrolled(self):
        return self.enrolled_for.filter(id=get_current_authenticated_user().pk).exists()
    
    def __str__(self):
    
        return self.title


class Module(models.Model):

    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    note = models.TextField()
    video_url = models.URLField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='geospatialhub/pdf/', blank=True, storage=RawMediaCloudinaryStorage())
    is_free_status = models.BooleanField(default=False)
    
    def __str__(self):
        
        return self.title


class CourseChat(models.Model):

    author = models.ForeignKey(User, related_name='coursechats', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='coursechats', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def get_sender_info(self):
        try:
           profile_pic = self.author.profile.profile_pic.url
        except:
            profile_pic = self.author.profile.profile_pic
        return {"id": self.author.id, "username": self.author.username, "first_name": self.author.profile.first_name, "last_name": self.author.profile.last_name,  "profile_pic": profile_pic}

    class Meta:
    
        ordering = ['-created']

    def __str__(self):

        return self.id

class Payment(models.Model):

    user = models.ForeignKey(User, related_name='payment', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='Payment', on_delete=models.CASCADE)
    reference = models.CharField(max_length=50,default='')
    amount = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    reversed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)