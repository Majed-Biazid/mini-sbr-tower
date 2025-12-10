from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import (
    UserReadSerializer,
    RegisterSerializer,
    UserUpdateSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Registration successful',
            'user': UserReadSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile.
    GET /api/auth/me/
    PATCH /api/auth/me/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserReadSerializer
        return UserUpdateSerializer


class LogoutView(APIView):
    """
    Logout user (client should delete tokens).
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Simple logout - client deletes tokens
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)