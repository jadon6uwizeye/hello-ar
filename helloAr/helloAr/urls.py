
from django.contrib import admin
from django.urls import path, include
from accounts import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import authentication

...

schema_view = get_schema_view(
   openapi.Info(
      title="Brainwave API",
      default_version='v1',
      description="This is the API documentation for the Brainwave API",
      terms_of_service="",
      contact=openapi.Contact(email="jeandedieuuwizeye6@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
       authentication_classes=(authentication.BasicAuthentication,),

   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('api/v1/auth/', include("accounts.urls")),
    path('api/v1/service/', include("service.urls")),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
