from django.urls import path
from . import views

urlpatterns = [
    path('google-login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google-callback/', views.GoogleCallbackView.as_view(), name='google_callback'),
]
