from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
)
from apps.audit_logs.utils import log_action


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get("username"))
            log_action(user, "LOGIN", "authentication.User", user.id, f"User {user.username} logged in")
        return response


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        log_action(request.user, "LOGOUT", "authentication.User", request.user.id, f"User {request.user.username} logged out")
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(self.request.user, "CREATE", "authentication.User", user.id, f"Created user {user.username}")


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
