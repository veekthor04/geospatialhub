from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework import viewsets, parsers
from rest_framework.parsers import JSONParser,FormParser, MultiPartParser
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly, IsPostOwner
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, PostRateSerializer, FollowerSerializer, MessageSerializer
from .models import Profile, Post, PostRate, Follower, Message
from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This displays the list of all users on the platform"
))
class UserViewSet(viewsets.ModelViewSet):
    
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)

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

    def get(self, request, pk):
        post = get_object_or_404(Post, pk = pk)
        data = {
            'likes_count': PostRate.objects.filter(liked = True, rated_post = post).count(), 
        }
        return Response(data)

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
    
    def get_queryset(self):
        return Post.objects.filter(in_reply_to_post = self.kwargs["pk"])

@api_view(['GET'])
def Follow(request, pk):
    user = get_object_or_404(get_user_model(), pk = pk)
    already_followed = Follower.objects.filter(user = user, is_followed_by = request.user).first()
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

class Following(generics.ListCreateAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), pk = self.kwargs["pk"])
        return Follower.objects.filter(is_followed_by = user)


class Followers(generics.ListCreateAPIView):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), pk = self.kwargs["pk"])
        return Follower.objects.filter(user = user).exclude(is_followed_by = user)

class MessageViewSet(viewsets.ModelViewSet):
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


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

    serializer = MessageSerializer(messages_array, many=True)
    return Response(serializer.data)

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