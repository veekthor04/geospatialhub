from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework import viewsets, parsers
from rest_framework.parsers import JSONParser,FormParser, MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly, IsPostOwner
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, PostRateSerializer, FollowerSerializer
from .models import Profile, Post, PostRate, Follower

# class UserList(generics.ListAPIView):

#     permission_classes = (permissions.AllowAny,)
#     queryset = get_user_model().objects.all()
#     serializer_class = UserSerializer

# class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    
#     permission_classes = (IsAuthorOrReadOnly,)
#     queryset = get_user_model().objects.all()
#     serializer_class = UserSerializer

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
            'dislikes_count': PostRate.objects.filter(liked = False, rated_post = post).count()
        }
        return Response(data)

    def post(self, request, pk, *args, **kwargs):
        # post = get_object_or_404(Post, pk = request.data["rated_post"]["id"])
        post = get_object_or_404(Post, pk = pk)
        post_rating = PostRate.objects.filter(rated_by = request.user, rated_post = post).first()
        user_liked_post = request.data["liked"]

        if post_rating:
            if user_liked_post:
                if post_rating.liked:
                    post_rating.liked = None
                else:
                    post_rating.liked = True                    
            elif not user_liked_post:
                if post_rating.liked == False:
                    post_rating.liked = None
                else:
                    post_rating.liked = False                    
        else:
            post_rating = PostRate(liked = user_liked_post, rated_by = request.user, rated_post = post)

        post_rating.save()

        data = {
            'total_likes': PostRate.objects.filter(liked = True, rated_post = post).count(), 
            'total_dislikes': PostRate.objects.filter(liked = False, rated_post = post).count()
        }
        return  Response(data)

class CommentList(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PostSerializer
    
    def get_queryset(self):
        return Post.objects.filter(in_reply_to_post = self.kwargs["pk"])

# @login_required
def Follow(request, pk):
    user = get_object_or_404(User, pk = pk)
    already_followed = Follower.objects.filter(user = user, is_followed_by = request.user).first()
    if not already_followed:
        new_follower = Follower(user = user, is_followed_by = request.user)
        new_follower.save()
        follower_count = Follower.objects.filter(user = user).count()
        return Response({'status': 'Following', 'count': follower_count})
    else:
        already_followed.delete()
        follower_count = Follower.objects.filter(user = user).count()
        return Response({'status': 'Not following', 'count': follower_count})

class Following(generics.ListCreateAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk = self.kwargs["pk"])
        return Follower.objects.filter(is_followed_by = user)


class Followers(generics.ListCreateAPIView):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk = self.kwargs["pk"])
        return Follower.objects.filter(user = user).exclude(is_followed_by = user)