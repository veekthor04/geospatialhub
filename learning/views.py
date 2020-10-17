from rest_framework import generics, permissions
from .models import Course, Module
from .serializers import CourseSerializer, SingleCourseSerializer

# Create your views here.
class ListCourse(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class DetailCourse(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = SingleCourseSerializer