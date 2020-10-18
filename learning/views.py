from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Course, Module
from .serializers import CourseSerializer, SingleCourseSerializer, FreeSingleCourseSerializer

# Create your views here.
class ListCourse(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# class DetailCourse(generics.RetrieveAPIView):
#     queryset = Course.objects.all()
#     serializer_class = SingleCourseSerializer

@api_view(['GET'])
def DetailCourse(request,pk):

    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user.profile.is_subscribed:
        serializer = SingleCourseSerializer(course)
    else:
        serializer = FreeSingleCourseSerializer(course)

    return Response(serializer.data)
