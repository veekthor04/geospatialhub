from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import RawMediaCloudinaryStorage


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
    estimated_time = models.IntegerField(help_text="Should be in minutes")
    created = models.DateTimeField(auto_now_add=True)
    enrolled_for = models.ManyToManyField(User, related_name='enrolled_for')
    
    class Meta:
    
        ordering = ['-created']

    def get_category(self):
        return {"id": self.category.id, "title": self.category.title}
    
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

    def __str__(self):

        return self.id