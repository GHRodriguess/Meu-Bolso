from .models import User
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        user = serializer.validated_data
        username = user.get('username')
        if not username:
            username = user.get('email').split('@')[0]
            
        serializer.save(username=username, is_active=True)
        