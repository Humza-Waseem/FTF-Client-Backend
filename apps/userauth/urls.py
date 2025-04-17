from django.urls import path, include
from .views import UserRegistrationView, CustomTokenObtainPairView, VerifyOTPView,PasswordResetView, SendOTPView, PerkvilleAuthView, PerkvilleOAuthCallbackView, PerkvillePasswordGrantView, PerkvilleUserInfoView
from django.conf import settings


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),    
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    # path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),

    # path('perkville/callback/', perkville_callback, name='perkville_callback'),
    # path('perkville/callback/', PerkvilleCallbackView.as_view(), name='perkville_callback'),
    path('perkville/auth/', PerkvilleAuthView.as_view(), name='perkville-auth'),
    path('perkville/callback/', PerkvilleOAuthCallbackView.as_view(), name='perkville-callback'),
    path('perkville/password-auth/', PerkvillePasswordGrantView.as_view(), name='perkville-password-auth'),
    path('perkville/user-info/', PerkvilleUserInfoView.as_view(), name='perkville-user-info'),


]