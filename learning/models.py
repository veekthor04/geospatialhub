from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):

    author = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    course_pic = models.ImageField(upload_to='course_pic/%Y/%m/%d/', max_length=255, null=True, blank=True)
    overview = models.TextField()
    estimated_time = models.IntegerField(help_text="Should be in minutes")
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
    
        ordering = ['-created']
    
    def __str__(self):
    
        return self.title

class Module(models.Model):

    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    note = models.TextField()
    video_url = models.URLField(null=True, blank=True)
    
    def __str__(self):
        
        return self.title