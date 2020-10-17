from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework import viewsets, parsers
from rest_framework.parsers import JSONParser,FormParser, MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly
from .serializers import UserSerializer, ProfileSerializer
from .models import Profile

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