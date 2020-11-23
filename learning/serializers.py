from rest_framework import serializers
from .models import Course, Module, CourseChat, Category


class CourseSerializer(serializers.ModelSerializer):

    module_count = serializers.SerializerMethodField()
    author = serializers.DictField(child = serializers.CharField(),source='get_author')
    category = serializers.DictField(child = serializers.CharField(),source='get_category')
    is_user_enrolled = serializers.BooleanField(source='get_is_user_enrolled')

    def get_module_count(self, course):
        return course.modules.count()

    class Meta:

        model = Course
        fields = ('id', 'author','category', 'title', 'course_pic', 'overview', 'estimated_time', 'price', 'price_before_discount', 'created', 'module_count', 'is_user_enrolled')

class CourseCategorySerializer(serializers.ModelSerializer):

    class Meta:

        model = Category
        fields = '__all__'

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
    # coursechats = CourseChatSerializer(many=True, read_only=True)
    category = serializers.DictField(child = serializers.CharField(),source='get_category')
    is_enrolled = serializers.BooleanField(source = 'get_is_user_enrolled', read_only = True)
    module_count = serializers.SerializerMethodField()

    def get_module_count(self, course):
        return course.modules.count()

    class Meta:

        model = Course
        fields = ('id', 'author', 'category', 'title', 'course_pic', 'overview', 'estimated_time', 'created','module_count','modules','is_enrolled')

class FreeSingleCourseSerializer(serializers.ModelSerializer):

    modules = serializers.SerializerMethodField('get_free')
    module_count = serializers.SerializerMethodField()
    category = serializers.DictField(child = serializers.CharField(),source='get_category')

    def get_module_count(self, course):
        return course.modules.count()

    def get_free(self, course):
        qs = Module.objects.filter(is_free_status=True, course=course)
        serializer = ModuleSerializer(instance=qs, many=True, read_only=True)
        return serializer.data

    class Meta:

        model = Course
        fields = ('id', 'author','category' , 'title', 'course_pic', 'overview', 'estimated_time', 'created','module_count' ,'modules')