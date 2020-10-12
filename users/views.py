from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from .permissions import IsAuthorOrReadOnly
from .serializers import UserSerializer

class UserList(generics.ListAPIView):

    permission_classes = (permissions.AllowAny,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer