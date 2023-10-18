from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import UserRegisterSerializer


class UserRegisterView(CreateAPIView):
    """Register a new user."""

    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
