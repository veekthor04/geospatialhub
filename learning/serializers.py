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

    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created','modules')

class FreeSingleCourseSerializer(serializers.ModelSerializer):

    modules = serializers.SerializerMethodField('get_free')

    def get_free(self, course):
        qs = Module.objects.filter(is_free_status=True, course=course)
        serializer = ModuleSerializer(instance=qs, many=True, read_only=True)
        return serializer.data

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created','modules')