from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
)



from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2LoginView, OAuth2CallbackView
)
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client
)


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = 'google'
    settings_key = 'SOCIALACCOUNT_PROVIDERS'

    def get_provider(self):
        return super(GoogleOAuth2Adapter, self).get_provider()

google_oauth2_adapter = GoogleOAuth2Adapter(request= None)

class GoogleLoginView(OAuth2LoginView):
    adapter_class = google_oauth2_adapter

class GoogleCallbackView(OAuth2CallbackView):
    adapter_class = google_oauth2_adapter

# class GoogleLogoutView(OAuth2LogoutView):
#     adapter_class = google_oauth2_adapter

@api_view(['POST'])
def google_login(request):
    access_token = request.data.get('access_token')

    provider = google_oauth2_adapter.get_provider()
    client = provider.client_class(request)

    try:
        token = client.parse_token({'access_token': access_token})
        login_result = provider.sociallogin_from_response(request, token)
        user = login_result.user

        if user:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data)
        else:
            return Response({'error': 'Authentication failed'}, status=400)
    except OAuth2Error as e:
        return Response({'error': str(e)}, status=400)

