from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, pagination, filters, mixins
from rest_framework.parsers import JSONParser,FormParser, MultiPartParser
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly, IsPostOwner
from .serializers import UserSerializer, ProfileSerializer, ListProfileSerializer, ListUserSerializer, PostSerializer, PostRateSerializer, FollowerSerializer, MyFollowerSerializer, MessageSerializer
from .models import Profile, Post, PostRate, Follower, Message
from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime

paginator = pagination.PageNumberPagination()
paginator.page_size = 20

class ProfileViewSet(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user = request.user).first()
        profile.first_name = request.data['first_name']
        profile.last_name = request.data['last_name']
        profile.phone = request.data['phone']
        profile.bio = request.data['bio']
        profile.date_of_birth = request.data['date_of_birth']
        profile.location_city = request.data['location_city']
        profile.location_state = request.data['location_state']
        profile.location_country = request.data['location_country']
        profile.organisation = request.data['organisation']
        profile.occupation = request.data['occupation']
        profile.institution = request.data['institution']
        profile.save()

        return Response({"response": "change successful"})

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user = request.user).first()
        try:
            profile.profile_pic = request.data['profile_pic']
        except:
            pass

        try:
            profile.banner_pic = request.data['banner_pic']
        except:
            pass

        profile.save()

        return Response({"response": "change successful"})

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This displays the list of all users on the platform"
))
class UserViewSet(viewsets.ModelViewSet):
    
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer



class ListUser(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = get_user_model().objects.all()
    serializer_class = ListUserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username', 'profile__first_name', 'profile__last_name')
    ordering_fields = ('profile__follower_count', 'profile__following_count')


    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="This shows the list of all users on the platform (lighter)"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="displays the sorted list of all post on the platform"
))
class PostViewSet(viewsets.ModelViewSet):
    
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPostOwner]
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('text',)    
    
    @action(detail=False, methods=['GET'], name='Get comments')
    def list_comments(self, request, *args, **kwargs):
        queryset = Post.objects.filter(in_reply_to_post = self.kwargs["pk"])
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_queryset(self):
        if self.action == 'list':
            return Post.objects.filter(in_reply_to_post = None)
        return Post.objects.all()

@swagger_auto_schema(
    method='get',
    responses={200: PostSerializer(many=True)},
    operation_description="displays the sorted list of all post for a user"
)
@api_view(['GET'])
def UserPost(request,pk):
    
    queryset = Post.objects.filter(posted_by=pk,in_reply_to_post = None)
    queryset_page = paginator.paginate_queryset(queryset, request)
    serializer = PostSerializer(queryset_page, many=True)
    return paginator.get_paginated_response(serializer.data)


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
            'status': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )},
    operation_description="The current user follows or unfollows a user"
)
@api_view(['GET'])
def Follow(request, pk):
    user = get_object_or_404(get_user_model(), pk = pk)
    
    if user != request.user:
        already_followed = Follower.objects.filter(user = user, is_followed_by  = request.user).first()
        if not already_followed:
            new_follower = Follower(user = user, is_followed_by = request.user)
            new_follower.save()
            profile = Profile.objects.get(user=user)
            profile.follower_count += 1
            profile.save()

            profile2 = Profile.objects.get(user=request.user)
            profile2.following_count += 1
            profile2.save()

            data={'status': 'Followed'}
            return Response(data=data)
        else:
            already_followed.delete()
            profile = Profile.objects.get(user=user)
            profile.follower_count -= 1
            profile.save()

            profile2 = Profile.objects.get(user=request.user)
            profile2.following_count -= 1
            profile2.save()

            data={'status': 'Unfollowed'}
            return Response(data=data)
    else:
        data={'status': 'you cannot follow yourself'}
        return Response(data=data)


class Following(generics.ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), pk = self.kwargs["pk"])
        return Follower.objects.filter(is_followed_by = user).exclude(user=user)
    
    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Displays the users the selected user is following"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = pagination.PageNumberPagination()
        queryset_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class Followers(generics.ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), pk = self.kwargs["pk"])
        return Follower.objects.filter(user = user).exclude(is_followed_by = user)
    
    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Displays the users following the selected user"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MyFollowing(generics.ListAPIView):
    serializer_class = FollowerSerializer
    def get_queryset(self):
        return Follower.objects.filter(is_followed_by=self.request.user).exclude(user=self.request.user)

    @method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Displays the users the current user is following"
    ))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset_page, many=True)
        return paginator.get_paginated_response(serializer.data)

@swagger_auto_schema(
    method='get',
    responses={200: MyFollowerSerializer(many=True)},
    operation_description="Displays the users following the current user"
)
@api_view(['GET'])
def MyFollowers(request):

    user = request.user
    
    followers = Follower.objects.filter(user=user).exclude(is_followed_by=user)

    message_page = paginator.paginate_queryset(followers, request)
    serializer = MyFollowerSerializer(message_page, many=True)

    for follower in followers:
        if follower.user==user and follower.is_viewed==False:
            follower.is_viewed = True
            follower.save()

    return paginator.get_paginated_response(serializer.data)

 
@swagger_auto_schema(
    method='get',
    responses={200: MessageSerializer(many=True)},
    operation_description="This displays last messages(paginated) between the current user and other users"
)
@api_view(['GET'])
def MessagesList(request):

    try:
        user_filter = request.query_params["search"]
    except:
         return Response(status=status.HTTP_404_NOT_FOUND)
    
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

    message_page = paginator.paginate_queryset(messages, request)
    serializer = MessageSerializer(message_page, many=True)

    for message in messages:
        if message.receiver==user and message.is_read==False:
            message.is_read = True
            message.save()

    return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'unread_message_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'new_follower': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    )},
    operation_description="This displays the number of unread messages and new followers"
)
@api_view(['GET'])
def Notification(request):

    user = request.user
    unread_count = Message.objects.filter(receiver=user, is_read=False).count()
    follower = Follower.objects.filter(user=user, is_viewed=False).exclude(is_followed_by = user)
    new_follower = []

    for follower in follower:
        pic = follower.is_followed_by.profile.profile_pic

        if not pic:
            pic = None

        new_follower.append({
            'id': follower.is_followed_by.id,
            'username': follower.is_followed_by.username,
            'first_name': follower.is_followed_by.first_name,
            'last_name': follower.is_followed_by.last_name,
            'profile_pic': pic,
            'created': follower.created,
        })
        
        delta = datetime.now().date() - follower.created.date()     

        if delta.days >= 1:
            follower.is_viewed = True
            follower.save()  


    return Response({'unread_message_count': unread_count, 'new_follower': new_follower})

@api_view(['GET'])
def Test(request):

    user = request.user
    follower = Follower.objects.filter(user=user, is_viewed=False).exclude(is_followed_by = user)
    myposts = Post.objects.filter(posted_by=user.id)
    notification = []

    for follower in follower:
        pic = follower.is_followed_by.profile.profile_pic.url

        if not pic:
            pic = None

        notification.append({
            'event': 'follow',
            'id': follower.is_followed_by.id,
            'username': follower.is_followed_by.username,
            'profile_pic': pic,
            'created': follower.created,
        })
    for post in myposts:
        pic = post.posted_by.profile.profile_pic.url

        if not pic:
            pic = None

        notification.append({
            'event': 'reply',
            'id': post.posted_by.id,
            'username': post.posted_by.username,
            'profile_pic': pic,
            'created': post.pub_date,
        })

    sorted(notification, key=notification['created'])
    
    print({'notification':notification})

    return Response({'notification':notification})


