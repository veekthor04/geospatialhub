from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, pagination
from rest_framework.parsers import JSONParser,FormParser, MultiPartParser
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly, IsPostOwner
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, PostRateSerializer, FollowerSerializer, MessageSerializer
from .models import Profile, Post, PostRate, Follower, Message
from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This displays the list of all users on the platform"
))
class UserViewSet(viewsets.ModelViewSet):
    
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    @swagger_auto_schema(
        method='put', 
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'profile_pic': openapi.Schema(type=openapi.TYPE_FILE)
            }
        ),
        responses={200: UserSerializer(many=False)},
        operation_description="to upload the user's profile pic"
    )
    @action(detail=True, methods=['put'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = user.profile
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, stutus=400)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="displays the sorted list of all post on the platform"
))
class PostViewSet(viewsets.ModelViewSet):
    
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPostOwner]
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    
    
    @action(detail=False, methods=['GET'], name='Get comments')
    def list_comments(self, request, *args, **kwargs):
        queryset = Post.objects.filter(in_reply_to_post = self.kwargs["pk"])
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_queryset(self):
        if self.action == 'list':
            return Post.objects.filter(in_reply_to_post = None).order_by('-pub_date')
        return Post.objects.order_by('-pub_date')


class PostRateViewSet(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = PostRate.objects.all()
    serializer_class = PostRateSerializer
    
    @swagger_auto_schema(
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'likes_count': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )},
        operation_description="Displays the number of likes for the selected post"
    )
    def get(self, request, pk):
        post = get_object_or_404(Post, pk = pk)
        data = {
            'likes_count': PostRate.objects.filter(liked = True, rated_post = post).count(), 
        }
        return Response(data)

    @swagger_auto_schema(
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'likes_count': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'liked': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            }
        ),
        operation_description="Likes or unlikes a post. Boolean True toggles the result"
    )
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk = pk)
        post_rating = PostRate.objects.filter(rated_by = request.user, rated_post = post).first()
        user_liked_post = request.data["liked"]

        if user_liked_post==True:
            if post_rating:
                if post_rating.liked:
                    post_rating.liked = False
                else:
                    post_rating.liked = True
            else:
                post_rating = PostRate(liked = user_liked_post, rated_by = request.user, rated_post = post)
        
            post_rating.save()

        data = {
            'total_likes': PostRate.objects.filter(liked = True, rated_post = post).count(), 
        }
        return  Response(data)


class CommentList(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PostSerializer
    
    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="displays the list of comments related to the selected post"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Post.objects.filter(in_reply_to_post = self.kwargs["pk"])

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING),
            'count': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    )},
    operation_description="The current user follows or unfollows a user"
)
@api_view(['GET'])
def Follow(request, pk):
    user = get_object_or_404(get_user_model(), pk = pk)
    already_followed = Follower.objects.filter(user = user, is_followed_by  = request.user).first()
    if not already_followed:
        new_follower = Follower(user = user, is_followed_by = request.user)
        new_follower.save()
        follower_count = Follower.objects.filter(user = user).count()
        data={'status': 'Following', 'count': follower_count}
        return Response(data=data)
    else:
        already_followed.delete()
        follower_count = Follower.objects.filter(user = user).count()
        data={'status': 'Not following', 'count': follower_count}
        return Response(data=data)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Displays the users the selected user is following"
))
class Following(generics.ListCreateAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), pk = self.kwargs["pk"])
        return Follower.objects.filter(is_followed_by = user)

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Displays the users following the selected user"
))
class Followers(generics.ListCreateAPIView):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), pk = self.kwargs["pk"])
        return Follower.objects.filter(user = user).exclude(is_followed_by = user)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Displays the users the selected user is following"
))
class MessageViewSet(viewsets.ModelViewSet):
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)
 
@swagger_auto_schema(
    method='get',
    responses={200: MessageSerializer(many=True)},
    operation_description="This displays last messages(paginated) between the current user and other users"
)
@api_view(['GET'])
def MessagesList(request):
    
    user = request.user
    messages = Message.objects.filter(Q(sender=user) | Q(receiver=user))
    messages_pal = []
    messages_array = []

    for message in messages:
        if message.sender==user and message.receiver not in messages_pal:
            messages_pal.append(message.receiver)
            messages_array.append(message)
        elif message.receiver==user and message.sender not in messages_pal:
            messages_pal.append(message.sender)
            messages_array.append(message)
    
    paginator = pagination.PageNumberPagination()
    paginator.page_size = 10
    message_page = paginator.paginate_queryset(messages_array, request)
    serializer = MessageSerializer(message_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method='get', 
    responses={200: MessageSerializer(many=True)},
    operation_description="This shows the chat between the current user and the selected user"
)
@swagger_auto_schema(
    method='post', 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: MessageSerializer(many=True)},
    operation_description="This adds a text to the chat between the current user and the selected user"
)
@api_view(['GET','POST'])
def SingleMessage(request,pk):

    try:
        user_pal = get_user_model().objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user

    if request.method == 'POST':

        text = request.data['text']

    
        message = Message.objects.create( sender=user, receiver=user_pal, text=text)
        message.save()
    
    messages = Message.objects.filter(Q(sender__in= [user,user_pal]) & Q(receiver__in= [user,user_pal]))

    for message in messages:
        if message.receiver==user:
            message.is_read = True
            message.save()

    serializer = MessageSerializer(messages, many=True)

    return Response(serializer.data)