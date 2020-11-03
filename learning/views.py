from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Course, Module, CourseChat, Category
from users.models import Profile
from .serializers import CourseSerializer, SingleCourseSerializer, FreeSingleCourseSerializer, CourseChatSerializer
from django_currentuser.middleware import get_current_authenticated_user


# Create your views here.
class ListCourse(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response_list = serializer.data 

        category_list =  Category.objects.all()

        all_categories = []
        for category in category_list:
            all_categories.append({"id": category.id, "title": category.title})

        data = { 'courses' : response_list, 'categories' : all_categories }
        return Response(data=data)


class ListEnrolledCourse(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(enrolled_for=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response_list = serializer.data 

        category_list =  Category.objects.all()

        all_categories = []
        for category in category_list:
            all_categories.append({"id": category.id, "title": category.title})

        data = { 'courses' : response_list, 'categories' : all_categories }
        return Response(data=data)


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
        serializer = SingleCourseSerializer(course)
        # print(Profile.objects.get(user=user).get_enrolled_for())
    else:
        serializer = FreeSingleCourseSerializer(course)

    return Response(serializer.data)
    
