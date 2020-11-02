from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Course, Module, CourseChat
from users.models import Profile
from .serializers import CourseSerializer, SingleCourseSerializer, FreeSingleCourseSerializer, CourseChatSerializer


# Create your views here.
class ListCourse(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# class DetailCourse(generics.RetrieveAPIView):
#     queryset = Course.objects.all()
#     serializer_class = SingleCourseSerializer

@api_view(['GET','POST'])
def DetailCourse(request,pk):

    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    body = request.data['body']
    enroll = request.data['enroll']
    
    if body:
    
        course_chat = CourseChat.objects.create( author=user, course=course, body=body)
        course_chat.save()

    if enroll == True:
            
        course.enrolled_for.add(user)

    if request.user.profile.is_subscribed:
        serializer = SingleCourseSerializer(course, context={'request': request})
        print(Profile.objects.get(user=user).get_enrolled_for)
    else:
        serializer = FreeSingleCourseSerializer(course, context={'request': request})

    return Response(serializer.data)
