from django.urls import path
from .views import UserViewSet, Post, PostRateViewSet, PostViewSet, CommentList
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'post', PostViewSet, basename='posts')

router.register('', UserViewSet, basename='users')

urlpatterns = [

    path('post/rate/<int:pk>/', PostRateViewSet.as_view(), name='rate'),
    path('post/retrieve-comments/<int:pk>/', CommentList.as_view(), name='retrieve-comments'),

]

urlpatterns += router.urls