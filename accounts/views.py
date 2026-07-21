from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, PhoneTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

User = get_user_model()   # accounts.User — never import django.contrib.auth.models.User now


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]   # public — overrides the global IsAuthenticated


class LoginView(TokenObtainPairView):
    """Login that normalizes Arabic/Persian digits in the phone number first."""
    serializer_class = PhoneTokenObtainPairSerializer


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()          # revoke it — can never be used again
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
