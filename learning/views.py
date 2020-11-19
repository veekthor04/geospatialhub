from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Course, Module, CourseChat, Category
from users.models import Profile
from .serializers import CourseSerializer, SingleCourseSerializer, FreeSingleCourseSerializer, CourseChatSerializer, CourseChatSerializer
from django_currentuser.middleware import get_current_authenticated_user
from random import choice
from string import digits, ascii_letters
from decouple import config
import requests


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
    
    if request.method == 'POST':

        user = request.user
        enroll = request.data['enroll']
        if enroll == True:
                
            course.enrolled_for.add(user)
        
        elif enroll == False:
                
            course.enrolled_for.remove(user)
        

    if course.enrolled_for.filter(id=request.user.pk).exists():
        serializer = SingleCourseSerializer(course)

    else:
        serializer = FreeSingleCourseSerializer(course)

    return Response(serializer.data)
    

@api_view(['GET','POST'])
def CourseChats(request,pk):

    try:
        course_chats = CourseChat.objects.filter(course=pk)
    except:
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':

        user = request.user
        text = request.data['text']

    
        course_chat = CourseChat.objects.create( author=user, course=Course.objects.get(pk=pk), body=text)
        course_chat.save()

    serializer = CourseChatSerializer(course_chats, many=True)

    return Response(serializer.data)
    

@api_view(['GET','POST'])
def Payment(request,pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    secret_key = config('PAYSTACK_SECRET_KEY',cast=str)
    headers = {'Authorization':secret_key}

    if request.method == 'POST':

        reference = request.data['reference']

        url = 'https://api.paystack.co/transaction/verify/' + reference

        r = requests.get    (url, headers=headers)

        if r.json()['data']['status'] == 'success':
            course.enrolled_for.add(user)

        return Response({'status':r.json()['data']['status']})

    reference = ''.join([choice(ascii_letters + digits) for n in range(16)])
    amount = course.price * 100
    email = user.email
    data = {'reference':reference,'amount':amount, 'email':email }
    url = 'https://api.paystack.co/transaction/initialize'

    r = requests.post(url, headers=headers, data=data)

    print(r.json()['data'])

    return Response(r.json()['data'])
    
