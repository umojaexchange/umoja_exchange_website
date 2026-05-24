from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SystemSettings
from .serializers import SystemSettingsSerializer

@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def settings_view(request):
    settings = SystemSettings.get()
    if request.method == "GET":
        return Response(SystemSettingsSerializer(settings).data)
    if not request.user.is_admin:
        return Response({"detail": "Only admins can update settings."}, status=status.HTTP_403_FORBIDDEN)
    serializer = SystemSettingsSerializer(settings, data=request.data, partial=request.method == "PATCH")
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
