from django.urls import path, include
from .views import UserRegistrationView, CustomTokenObtainPairView, VerifyOTPView,PasswordResetView, SendOTPView
# PerkvilleAuthView, PerkvilleOAuthCallbackView, PerkvillePasswordGrantView, PerkvilleUserInfoView,

from django.conf import settings

from .views import RegistrationErrorView
from django.views.generic import TemplateView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),    
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
]