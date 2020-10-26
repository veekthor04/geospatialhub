from rest_framework import serializers
from .models import Course, Module, CourseChat


class CourseSerializer(serializers.ModelSerializer):

    module_count = serializers.SerializerMethodField()

    def get_module_count(self, course):
        return course.modules.count()

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created', 'module_count')


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:

        model = Module
        fields = ('id', 'title', 'description', 'note', 'video_url', 'pdf_file')


class CourseChatSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        
        model = CourseChat
        fields = ('author', 'username', 'body', 'created')


class SingleCourseSerializer(serializers.ModelSerializer):

    modules = ModuleSerializer(many=True, read_only=True)
    coursechats = CourseChatSerializer(many=True, read_only=True)

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created','modules', 'coursechats')

class FreeSingleCourseSerializer(serializers.ModelSerializer):

    modules = serializers.SerializerMethodField('get_free')

    def get_free(self, course):
        qs = Module.objects.filter(is_free_status=True, course=course)
        serializer = ModuleSerializer(instance=qs, many=True, read_only=True)
        return serializer.data

    class Meta:

        model = Course
        fields = ('id', 'author', 'title', 'course_pic', 'overview', 'estimated_time', 'created','modules')