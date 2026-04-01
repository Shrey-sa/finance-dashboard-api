from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .permissions import IsAdmin, IsActiveUser
from .serializers import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer, ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """Public registration — always creates a Viewer. Admins use UserViewSet."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(role='viewer')  # force viewer on public register
        return Response(
            {'success': True, 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )


class MeView(generics.RetrieveUpdateAPIView):
    """Current user profile."""
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Users can only update their own full_name
        serializer = UserSerializer(
            request.user, data={'full_name': request.data.get('full_name', request.user.full_name)},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'user': serializer.data})


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'success': True, 'message': 'Password updated successfully.'})


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only user management."""
    queryset = User.objects.all().order_by('date_joined')
    permission_classes = [IsAuthenticated, IsActiveUser, IsAdmin]

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'success': True, 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'success': True, 'is_active': user.is_active})

    @action(detail=True, methods=['patch'], url_path='set-role')
    def set_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get('role')
        from .models import Role
        if role not in Role.values:
            return Response(
                {'success': False, 'errors': {'role': f'Must be one of: {Role.values}'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.role = role
        user.save()
        return Response({'success': True, 'role': user.role})
