from django.urls import path
from .views import UserViewSet, Post, PostRateViewSet, PostViewSet, CommentList, Follow, Followers, Following, MessageViewSet, MessagesList, SingleMessage
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'post', PostViewSet, basename='posts')
router.register(r'message', MessageViewSet, basename='message')

router.register('', UserViewSet, basename='users')

urlpatterns = [

    path('post/rate/<int:pk>/', PostRateViewSet.as_view(), name='rate'),
    path('post/retrieve-comments/<int:pk>/', CommentList.as_view(), name='retrieve-comments'),

    path('follow/<int:pk>/', Follow, name='follow'),
    path('following/<int:pk>/', Following.as_view(), name='following'),
    path('followers/<int:pk>/', Followers.as_view(), name='followers'),
    
    path('chats/', MessagesList, name='chats'),
    path('chats/<int:pk>/', SingleMessage, name='single-chats'),
    
]

urlpatterns += router.urls