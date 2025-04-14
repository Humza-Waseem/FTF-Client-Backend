from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, VerifyOTPSerializer, OTPVerificationSerializer
from django.utils import timezone
from rest_framework.views import APIView
# from .services import create_mindbody_user
from rest_framework.permissions import AllowAny
from rest_framework import status, generics, serializers
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from django.utils.encoding import force_bytes, force_str
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model  
from rest_framework.authtoken.models import Token  
import logging
from django.db import transaction  #importing this because we're ensuring data integrity
from .emails import *
from django.core.cache import cache

from django.contrib.auth import authenticate
from apps.userauth.Services.Mindbody import MindbodyAPI
from apps.userauth.Services.Inbody import InbodyAPI

 
        
User = get_user_model()   # getting the user model

logger = logging.getLogger(__name__)

            
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            # Call Mindbody API to add the client
            mindbody = MindbodyAPI()
            mindbody_response = mindbody.create_mindbody_client(validated_data)
            print("Mindbody Response:", mindbody_response)

            # Check if client was successfully created in Mindbody
            if not mindbody_response or 'Client' not in mindbody_response or not mindbody_response.get('Client', {}).get('Id'):
                return Response(
                    {'error': 'Failed to create user in Mindbody', 'details': mindbody_response},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"User created in Mindbody: {mindbody_response}")

            # Get Mindbody ID from response
            mindbody_id = mindbody_response['Client']['Id']

            ########## INBODY API CALL ##############
            inbody = InbodyAPI()
            inbody_response = inbody.create_inbody_user(validated_data)
            print("InBody Response:", inbody_response)

            # Check if client was successfully created in Inbody
            if not inbody_response:
                return Response(
                    {'error': 'Failed to create user in InBody', 'details': inbody_response},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"User created in InBody: {inbody_response}")

            # Get phone number for Inbody ID
            inbody_id = validated_data['phone_number']

            # Save user locally with both IDs
            user = serializer.save(
                mindbody_id=mindbody_id,
                inbody_id=inbody_id
            )

            send_otp_via_email(user.email, request=request)

            return Response({
                'message': "User registered successfully. OTP sent to your email for verification.",
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'City': user.City,
                    'State': user.State,
                    'Country': user.Country,
                    'PostalCode': user.PostalCode,
                    'AddressLine1': user.AddressLine1,
                    'ReferredBy': user.ReferredBy,
                    'DateOfBirth': user.DateOfBirth,
                    'PhoneNumber': user.phone_number,
                    'mindbody_id': mindbody_id,  # From Mindbody response
                    'inbody_id': inbody_id,      # Phone number used as Inbody ID
                    'Height': user.Height,
                    'Weight': user.Weight,
                }
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
            
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
            
            
            
            
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data['email']
        otp_input = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
            
            #checkinng if email is already verified
            if (user.is_email_verified):
                return Response({
                    "message": "Email already verified."
                }, status=status.HTTP_200_OK)
            
            
            if not user.otp_secret_key or not user.otp_valid_until:
                return Response({
                    "error": "Verification code has expired or doesn't exist. Please request a new one."
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if timezone.now() > user.otp_valid_until:
                return Response({
                    "error": "Verification code has expired. Please request a new one."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use TOTP verification with a window to allow for slight time differences
            # Window of 1 allows checking the current and previous interval
            totp = pyotp.TOTP(user.otp_secret_key, interval=30)
            if totp.verify(otp_input, valid_window=1):
                # Mark user as verified
                user.is_email_verified = True
                
                # Clear OTP data for security
                user.otp_secret_key = None
                user.otp_valid_until = None
                user.save()
                
                return Response({
                    "message": "Email verified successfully."
                }, status=status.HTTP_200_OK)
            
            # Invalid OTP
            return Response({
                "error": "Invalid verification code. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response({
                "error": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
            












#################################      NEW IMPLEMENTATION      #########################


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Create user in Mindbody
        mindbody = MindbodyAPI()
        mindbody_response = mindbody.create_mindbody_client(data)
        if mindbody_response.get('Status') != 'Success':
            return Response({'error': 'Failed to create user in Mindbody'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Create user in Django
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mindbody_id=mindbody_response['Clients'][0]['Id']  # Store Mindbody ID
        )
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
    
    
    
    
    
    
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate with Mindbody
        mindbody = MindbodyAPI()
        mindbody_response = mindbody.validate_login(email, password)
        if mindbody_response.get('Status') != 'Success':
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Authenticate with Django
        user = authenticate(username=email, password=password)
        if not user:
            # Sync user with Django if not already present
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                mindbody_id=mindbody_response['Client'][0]['ID']
            )

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
        

class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')

        # Trigger password reset in Mindbody
        mindbody = MindbodyAPI()
        mindbody_response = mindbody.reset_password(email)
        if mindbody_response.get('Status') != 'Success':
            return Response({'error': 'Failed to reset password in Mindbody'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
    
    
import pyotp
from django.utils import timezone
from datetime import timedelta

class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            secret_key = pyotp.random_base32()
            otp = pyotp.TOTP(secret_key, interval=300).now()  # OTP valid for 5 minutes
            user.otp_secret_key = secret_key
            user.otp_valid_until = timezone.now() + timedelta(minutes=5)
            user.save()

            # Send OTP via email
            send_otp_via_email(email, otp)

            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

