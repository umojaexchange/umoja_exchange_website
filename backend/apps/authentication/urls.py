from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, logout_view, me_view, UserListCreateView, UserDetailView, change_password_view

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", me_view, name="me"),
    path("users/", UserListCreateView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("change-password/", change_password_view, name="change-password"),
]
