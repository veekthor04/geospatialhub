from rest_framework import generics, permissions, status, pagination, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Course, Module, CourseChat, Category, Payment as PaymentModel
from users.models import Profile, Notification
from .serializers import CourseSerializer, CourseCategorySerializer, SingleCourseSerializer, FreeSingleCourseSerializer, CourseChatSerializer, CourseChatSerializer
from django_currentuser.middleware import get_current_authenticated_user
from random import choice
from string import digits, ascii_letters
from decouple import config
import requests
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import datetime

paginator = pagination.PageNumberPagination()
paginator.page_size = 20

# Create your views here.

class ListCourse(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'overview', 'category__title')
    ordering_fields = ('title', 'created')

    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This shows the list of all courses on the platform"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ListCourseCategory(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CourseCategorySerializer

    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This shows the list of all course categories on the platform"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset_page = paginator.paginate_queryset(queryset, request)
        paginator.page_size = 1000000
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ListEnrolledCourse(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'overview', 'category__title')
    ordering_fields = ('title', 'created')

    def get_queryset(self):
        return Course.objects.filter(enrolled_for=self.request.user)

    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This shows the list of all courses the current user is enrolled for"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method='get', 
    responses={200: SingleCourseSerializer(many=False)},
    operation_description="This shows the details of the selected course"
)
@api_view(['GET'])
def DetailCourse(request,pk):

    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if course.enrolled_for.filter(id=request.user.pk).exists():

        serializer = SingleCourseSerializer(course)

    else:
        serializer = FreeSingleCourseSerializer(course)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'unenroll_status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'refund_status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'message': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )},
    operation_description="This unerolls a user from a cousre, checks if the user has not been refunded before and checks if it is within 14 days before carrying out a refund"
)
@api_view(['GET',])
def DetailCourseUnenroll(request,pk):

    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    secret_key = config('PAYSTACK_SECRET_KEY',cast=str)
    headers = {'Authorization':secret_key}

    course.enrolled_for.remove(user)
    
    Notification.objects.create(course=course, user=user, event="unenroll_course")

    try:
        course_payment = PaymentModel.objects.get( user=user, course=course)
    except PaymentModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    delta = datetime.datetime.now().date() - course_payment.created.date()     

    if delta.days <= 14 and course_payment.reversed == False:

        secret_key = config('PAYSTACK_SECRET_KEY',cast=str)
        headers = {'Authorization':secret_key}
        
        reference = course_payment.reference
        amount = course_payment.amount
        email = user.email
        data = {'transaction':reference,'amount':amount, 'email':email }
        url = 'https://api.paystack.co/refund'

        course_payment.reversed = True
        course_payment.save()

        r = requests.post(url, headers=headers, data=data)

        data = {"unenroll_status": True, "refund_status": r.json()['status'], "message": r.json()['message']}
    
    elif delta.days > 14 and course_payment.reversed == False:
        data = {"unenroll_status": True, "refund_status": False, "message": "Course paymnet cannot be reversed after 14 days"}
    
    else:
        data = {"unenroll_status": True, "refund_status": False, "message": "Course paymnet can only be reversed once"}
        
    return Response(data)
    

@swagger_auto_schema(
    method='get', 
    responses={200: CourseChatSerializer(many=True)},
    operation_description="This shows the chat for the selected course"
)
@swagger_auto_schema(
    method='post', 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: CourseChatSerializer(many=True)},
    operation_description="This adds a text to the chat for the selected course "
)
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

    queryset_page = paginator.paginate_queryset(course_chats, request)
    serializer = CourseChatSerializer(queryset_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
            openapi.Parameter(
                name='callback_url', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Redirect link after paymnet",
                required=True
            ),
        ], 
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'authorization_url': openapi.Schema(type=openapi.TYPE_STRING),
            'access_code': openapi.Schema(type=openapi.TYPE_STRING),
            'reference': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )},
    operation_description="This shows payment infos including the payment link"
)
@api_view(['GET',])
def Payment(request,pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    secret_key = config('PAYSTACK_SECRET_KEY',cast=str)
    headers = {'Authorization':secret_key}

    reference = ''.join([choice(ascii_letters + digits) for n in range(16)])
    amount = course.price * 100
    email = user.email
    
    try:
        callback_url = request.query_params["callback_url"]
    except:
         return Response(status=status.HTTP_404_NOT_FOUND)

    # currency = 'USD'
    # data = {'reference':reference,'amount':amount, 'email':email, 'currency':currency, 'callback_url': callback_url}

    data = {'reference':reference,'amount':amount, 'email':email, 'callback_url': callback_url}

    url = 'https://api.paystack.co/transaction/initialize'

    if not PaymentModel.objects.filter(user=user, course=course).exists():
        course_payment = PaymentModel.objects.create( user=user, course=course, reference=reference, amount=amount)
        course_payment.save()
    else:
        course_payment = PaymentModel.objects.get(user=user, course=course)
        course_payment.completed = False
        course_payment.amount = amount
        course_payment.reference = reference 
        course_payment.save()
        

    r = requests.post(url, headers=headers, data=data)

    print(r.json()['data'])

    return Response(r.json()['data'])


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )},
    operation_description="This shows is a payment was completed"
)
@api_view(['GET',])
def PaymentConfirm(request,pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    secret_key = config('PAYSTACK_SECRET_KEY',cast=str)
    headers = {'Authorization':secret_key}

    try:
        course_payment = PaymentModel.objects.get( user=user, course=course)
    except PaymentModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    reference = course_payment.reference

    url = 'https://api.paystack.co/transaction/verify/' + reference

    r = requests.get(url, headers=headers)

    if r.json()['data']['status'] == 'success':
        course.enrolled_for.add(user)

        course_payment.completed = True
        course_payment.save()
    
        Notification.objects.create(course=course, user=user, event="new_course")        

    return Response({'status':r.json()['data']['status']})
    
