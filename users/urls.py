from django.urls import path
from .views import UserViewSet, ProfileViewSet, ListUser, Post, UserPost, PostRateViewSet, PostViewSet, CommentList, Follow, Followers, Following, MyFollowers, MyFollowing, MessagesList, SingleMessage, Notification
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'post', PostViewSet, basename='posts')
router.register('', UserViewSet, basename='users')

urlpatterns = [

    path('profile/<int:pk>/', ProfileViewSet.as_view(), name='users'),
    path('list-all/', ListUser.as_view(), name='list user'),

    path('post/rate/<int:pk>/', PostRateViewSet.as_view(), name='rate'),
    path('post/retrieve-comments/<int:pk>/', CommentList.as_view(), name='retrieve-comments'),
    path('<int:pk>/post/', UserPost, name='user-post'),

    path('follow/<int:pk>/', Follow, name='follow'),
    path('following/<int:pk>/', Following.as_view(), name='following'),
    path('followers/<int:pk>/', Followers.as_view(), name='followers'),
    path('myfollowing/', MyFollowing.as_view(), name='myfollowing'),
    path('myfollowers/', MyFollowers, name='myfollowers'),
    
    path('chats/', MessagesList, name='chats'),
    path('chats/<int:pk>/', SingleMessage, name='single-chats'),

    path('notification/', Notification, name='notifications')
    
]

urlpatterns += router.urls