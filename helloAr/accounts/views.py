# authentication/views.py

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from rest_framework import generics, permissions
from rest_framework.response import Response


from accounts.serializers import UserSerializer

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # callback_url = "http://localhost:8000/"
    client_class = OAuth2Client


class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    # callback_url = "http://localhost:8000/"
    client_class = OAuth2Client


# userView to return user data
class UserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user