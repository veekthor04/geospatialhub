from rest_framework import serializers
from .models import Course, Module


class CourseSerializer(serializers.ModelSerializer):

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created')

class ModuleSerializer(serializers.ModelSerializer):

    class Meta:

        model = Module
        fields = ('id', 'title', 'description', 'note', 'video_url')

class SingleCourseSerializer(serializers.ModelSerializer):

    # module = ModuleSerializer()

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created',)