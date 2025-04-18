from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, VerifyOTPSerializer, OTPVerificationSerializer, PasswordResetSerializer
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.decorators import api_view
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
from django.db import transaction  #?importing this because we're ensuring data integrity
from .emails import *
from django.core.cache import cache

from django.contrib.auth import authenticate
from apps.userauth.Services.Mindbody import MindbodyAPI
from apps.userauth.Services.Inbody import InbodyAPI
# from apps.userauth.Services.perkville import get_perkville_authorization_url
import uuid
import urllib.parse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from apps.userauth.utils.perkville import get_perkville_authorization_url



User = get_user_model()   
logger = logging.getLogger(__name__)
          
            
            #  Generate a state and build Perkville auth URL
            # state = str(uuid.uuid4())
            # request.session['perkville_oauth_state'] = state

            # query_params = {
            #     'client_id': settings.PERKVILLE_CLIENT_ID,
            #     'redirect_uri': settings.PERKVILLE_REDIRECT_URI,
            #     'response_type': 'code',
            #     'scope': 'PUBLIC USER_CUSTOMER_INFO USER_REDEEM',
            #     'state': state
            # }

            # auth_url = f"{settings.PERKVILLE_AUTH_URL}?{urllib.parse.urlencode(query_params)}"
            
        


            
# class UserRegistrationView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserRegistrationSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#             validated_data = serializer.validated_data

#             # Call Mindbody API to add the client
#             mindbody = MindbodyAPI()
#             mindbody_response = mindbody.create_mindbody_client(validated_data)
#             print("Mindbody Response:", mindbody_response)

#             # Check if client was successfully created in Mindbody
#             if not mindbody_response or 'Client' not in mindbody_response or not mindbody_response.get('Client', {}).get('Id'):
#                 return Response(
#                     {'error': 'Failed to create user in Mindbody', 'details': mindbody_response},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             logger.info(f"User created in Mindbody: {mindbody_response}")

#             # Get Mindbody ID from response
#             mindbody_id = mindbody_response['Client']['Id']

#             ########## INBODY API CALL ##############
#             inbody = InbodyAPI()
#             inbody_response = inbody.create_inbody_user(validated_data)
#             print("InBody Response:", inbody_response)

#             # Check if client was successfully created in Inbody
#             if not inbody_response:
#                 return Response(
#                     {'error': 'Failed to create user in InBody', 'details': inbody_response},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             logger.info(f"User created in InBody: {inbody_response}")

#             # Get phone number for Inbody ID
#             inbody_id = validated_data['phone_number']

#             # Save user locally with both IDs
#             user = serializer.save(
#                 mindbody_id=mindbody_id,
#                 inbody_id=inbody_id
#             )

#             send_otp_via_email(user.email, request=request)

#             return Response({
#                 'message': "User registered successfully. OTP sent to your email for verification.",
                
#                 'perkville_redirect_url': perkville_redirect_url,
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name,
#                     'City': user.City,
#                     'State': user.State,
#                     'Country': user.Country,
#                     'PostalCode': user.PostalCode,
#                     'AddressLine1': user.AddressLine1,
#                     'ReferredBy': user.ReferredBy,
#                     'DateOfBirth': user.DateOfBirth,
#                     'Gender': user.Gender,
#                     'PhoneNumber': user.phone_number,
#                     'mindbody_id': mindbody_id,  # From Mindbody response
#                     'inbody_id': inbody_id,      # Phone number used as Inbody ID
#                     'Height': user.Height,
#                     'Weight': user.Weight,
#                 }
#             }, status=status.HTTP_201_CREATED)

#         except serializers.ValidationError as e:
#             return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)


# class UserRegistrationView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserRegistrationSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#             validated_data = serializer.validated_data

#             # Mindbody
#             mindbody = MindbodyAPI()
#             mindbody_response = mindbody.create_mindbody_client(validated_data)
#             print("Mindbody Response:", mindbody_response)

#             if not mindbody_response or 'Client' not in mindbody_response or not mindbody_response.get('Client', {}).get('Id'):
#                 return Response(
#                     {'error': 'Failed to create user in Mindbody', 'details': mindbody_response},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             logger.info(f"User created in Mindbody: {mindbody_response}")
#             mindbody_id = mindbody_response['Client']['Id']

#             # InBody
#             inbody = InbodyAPI()
#             inbody_response = inbody.create_inbody_user(validated_data)
#             print("InBody Response:", inbody_response)

#             if not inbody_response:
#                 return Response(
#                     {'error': 'Failed to create user in InBody', 'details': inbody_response},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             logger.info(f"User created in InBody: {inbody_response}")
#             inbody_id = validated_data['phone_number']

#             # Save user
#             user = serializer.save(
#                 mindbody_id=mindbody_id,
#                 inbody_id=inbody_id
#             )

#             send_otp_via_email(user.email, request=request)

#             # Perkville OAuth redirect URL
#             perkville_redirect_url = get_perkville_authorization_url()

#             return Response({
#                 'message': "User registered successfully. OTP sent to your email for verification.",
#                 'perkville_redirect_url': perkville_redirect_url,
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name,
#                     'City': user.City,
#                     'State': user.State,
#                     'Country': user.Country,
#                     'PostalCode': user.PostalCode,
#                     'AddressLine1': user.AddressLine1,
#                     'ReferredBy': user.ReferredBy,
#                     'DateOfBirth': user.DateOfBirth,
#                     'Gender': user.Gender,
#                     'PhoneNumber': user.phone_number,
#                     'mindbody_id': mindbody_id,
#                     'inbody_id': inbody_id,
#                     'Height': user.Height,
#                     'Weight': user.Weight,
#                 }
#             }, status=status.HTTP_201_CREATED)

#         except serializers.ValidationError as e:
#             return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)


######## REGISTER VIEW
# class UserRegistrationView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserRegistrationSerializer

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.validate_user_data(request)
            
#             mindbody_id = self.create_mindbody_user(serializer.validated_data)
            
#             inbody_id = self.create_inbody_user(serializer.validated_data)
            
#             user = self.save_user(serializer, mindbody_id, inbody_id)
            
#             self.send_otp_email(user)
            
#             return self.prepare_success_response(user, mindbody_id, inbody_id)

#         except serializers.ValidationError as e:
#             return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)

#     def validate_user_data(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return serializer

#     def create_mindbody_user(self, validated_data):
#         mindbody = MindbodyAPI()
#         mindbody_response = mindbody.create_mindbody_client(validated_data)
#         logger.info(f"Mindbody Response: {mindbody_response}")

#         if not mindbody_response or 'Client' not in mindbody_response or not mindbody_response.get('Client', {}).get('Id'):
#             raise serializers.ValidationError(
#                 {'error': 'Failed to create user in Mindbody', 'details': mindbody_response}
#             )

#         logger.info(f"User created in Mindbody: {mindbody_response}")
#         return mindbody_response['Client']['Id']

#     def create_inbody_user(self, validated_data):
#         inbody = InbodyAPI()
#         inbody_response = inbody.create_inbody_user(validated_data)
#         logger.info(f"InBody Response: {inbody_response}")

#         if not inbody_response:
#             raise serializers.ValidationError(
#                 {'error': 'Failed to create user in InBody', 'details': inbody_response}
#             )

#         logger.info(f"User created in InBody: {inbody_response}")
#         return validated_data['phone_number']  

#     def save_user(self, serializer, mindbody_id, inbody_id):
#         return serializer.save(
#             mindbody_id=mindbody_id,
#             inbody_id=inbody_id
#         )

#     def send_otp_email(self, user):
#         send_otp_via_email(user.email, request=self.request)

#     def prepare_success_response(self, user, mindbody_id, inbody_id):
#         perkville_redirect_url = get_perkville_authorization_url()
        
#         return Response({
#             'message': "User registered successfully. OTP sent to your email for verification.",
#             'perkville_redirect_url': perkville_redirect_url,
#             'user': {
#                 'id': user.id,
#                 'email': user.email,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'City': user.City,
#                 'State': user.State,
#                 'Country': user.Country,
#                 'PostalCode': user.PostalCode,
#                 'AddressLine1': user.AddressLine1,
#                 'ReferredBy': user.ReferredBy,
#                 'DateOfBirth': user.DateOfBirth,
#                 'Gender': user.Gender,
#                 'PhoneNumber': user.phone_number,
#                 'mindbody_id': mindbody_id,
#                 'inbody_id': inbody_id,
#                 'Height': user.Height,
#                 'Weight': user.Weight,
#             }
#         }, status=status.HTTP_201_CREATED)       
        
        
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            # Validate input data
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            # Create Mindbody user
            mindbody = MindbodyAPI()
            mindbody_response = mindbody.create_mindbody_client(validated_data)
            logger.info("Mindbody Response: %s", mindbody_response)

            if not mindbody_response or 'Client' not in mindbody_response or not mindbody_response.get('Client', {}).get('Id'):
                return Response(
                    {'error': 'Failed to create user in Mindbody', 'details': mindbody_response},
                    status=status.HTTP_400_BAD_REQUEST
                )
            mindbody_id = mindbody_response['Client']['Id']

            # Create InBody user
            inbody = InbodyAPI()
            inbody_response = inbody.create_inbody_user(validated_data)
            logger.info("InBody Response: %s", inbody_response)

            if not inbody_response:  # Your original check that was working
                return Response(
                    {'error': 'Failed to create user in InBody', 'details': inbody_response},
                    status=status.HTTP_400_BAD_REQUEST
                )
            inbody_id = validated_data['phone_number']

            # Save local user
            user = serializer.save(
                mindbody_id=mindbody_id,
                inbody_id=inbody_id
            )

            # Send OTP email
            send_otp_via_email(user.email, request=request)

            # Generate Perkville OAuth URL
            try:
                auth_url, _ = PerkvilleService.get_authorization_url(request)
            except Exception as e:
                logger.error("Perkville URL generation failed: %s", str(e))
                auth_url = None

            # Build response
            response_data = {
                'message': "User registered successfully. OTP sent to your email.",
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'PhoneNumber': user.phone_number,
                    'mindbody_id': mindbody_id,
                    'inbody_id': inbody_id,
                }
            }

            if auth_url:
                response_data['perkville_redirect_url'] = auth_url
            else:
                response_data['warning'] = "Perkville integration temporarily unavailable"

            return Response(response_data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            logger.error("Validation error: %s", str(e))
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return Response(
                {'error': 'Registration failed - please try again'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from apps.userauth.Services.Perkville import PerkvilleService
@api_view(['GET'])
def perkville_callback(request):
    try:
        # 1. Verify state and get token
        access_token = PerkvilleService.exchange_code_for_token(
            code=request.GET.get('code'),
            state=request.GET.get('state'),
            request=request
        )
        
        # 2. Store token with user
        request.user.perkville_access_token = access_token
        request.user.save()
        
        # 3. Redirect to success page
        return redirect('registration-success')
        
    except Exception as e:
        logger.error(f"Perkville callback failed: {str(e)}")
        return redirect('registration-error?message=' + str(e))

####### LOGIN VIEW
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    









# class MindbodyPasswordResetView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get('email')
#         first_name = request.data.get('first_name')
#         last_name = request.data.get('last_name')

#         if not email or not first_name or not last_name:
#             return Response(
#                 {"error": "Email, first name, and last name are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         mindbody = MindbodyAPI()
#         response = mindbody.send_password_reset_email(email, first_name, last_name)

#         if response.get("success"):
#             return Response(
#                 {"message": "Password reset email sent successfully."},
#                 status=status.HTTP_200_OK
#             )
#         else:
#             return Response(
#                 {"error": response.get("error"), "details": response.get("message")},
#                 status=response.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
#             )


















# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# import requests
# from django.conf import settings

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def perkville_callback(request):
#     code = request.GET.get('code')
#     state = request.GET.get('state')

#     if state != request.session.get('perkville_oauth_state'):
#         return Response({'error': 'Invalid OAuth state'}, status=400)

#     data = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': settings.PERKVILLE_REDIRECT_URI,
#         'client_id': settings.PERKVILLE_CLIENT_ID,
#     }

#     auth = (settings.PERKVILLE_CLIENT_ID, settings.PERKVILLE_CLIENT_SECRET)
#     res = requests.post(settings.PERKVILLE_TOKEN_URL, data=data, auth=auth)

#     if res.status_code != 200:
#         return Response({'error': 'Failed to exchange code for token'}, status=500)

#     access_token = res.json().get('access_token')

#     return Response({'message': 'Perkville Connected', 'token': access_token})
           
            
            
            
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


# class RegisterView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserRegistrationSerializer
#     def post(self, request):
#         data = request.data
#         email = data.get('email')
#         password = data.get('password')
#         first_name = data.get('first_name')
#         last_name = data.get('last_name')

#         # Create user in Mindbody
#         mindbody = MindbodyAPI()
#         mindbody_response = mindbody.create_mindbody_client(data)
#         if mindbody_response.get('Status') != 'Success':
#             return Response({'error': 'Failed to create user in Mindbody'}, status=status.HTTP_400_BAD_REQUEST)
        

#         # Create user in Django
#         user = User.objects.create_user(
#             username=email,
#             email=email,
#             password=password,
#             first_name=first_name,
#             last_name=last_name,
#             mindbody_id=mindbody_response['Clients'][0]['Id']  # Store Mindbody ID
#         )
#         return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
    
    
    
    
    

# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         # Authenticate with Mindbody
#         mindbody = MindbodyAPI()
#         mindbody_response = mindbody.validate_login(email, password)
#         if mindbody_response.get('Status') != 'Success':
#             return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#         # Authenticate with Django
#         user = authenticate(username=email, password=password)
#         if not user:
#             # Sync user with Django if not already present
#             user = User.objects.create_user(
#                 username=email,
#                 email=email,
#                 password=password,
#                 mindbody_id=mindbody_response['Client'][0]['ID']
#             )

#         # Generate JWT token
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'access': str(refresh.access_token),
#             'refresh': str(refresh),
#         }, status=status.HTTP_200_OK)
        

# class PasswordResetView(APIView):
#     def post(self, request):
#         email = request.data.get('email')

#         # Trigger password reset in Mindbody
#         mindbody = MindbodyAPI()
#         mindbody_response = mindbody.reset_password(email)
#         if mindbody_response.get('Status') != 'Success':
#             return Response({'error': 'Failed to reset password in Mindbody'}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
    
    
import pyotp
from django.utils import timezone
from datetime import timedelta

class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            secret_key = pyotp.random_base32()
            otp = pyotp.TOTP(secret_key, interval=300).now()  
            user.otp_secret_key = secret_key
            user.otp_valid_until = timezone.now() + timedelta(minutes=5)
            user.save()

            send_otp_via_email(email, otp)

            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .Services.Mindbody import MindbodyAPI

class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        
        mindbody_api = MindbodyAPI()
        response = mindbody_api.send_password_reset_email(email, first_name, last_name)
        
        if response.get("success"):
            return Response(
                {"message": "Password reset email sent successfully.", "details": response.get("data")},
                status=status.HTTP_200_OK
            )
        else:
            error_status = response.get("status_code")
            if error_status and isinstance(error_status, int) and 400 <= error_status < 600:
                response_status = error_status
            else:
                response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
                
            return Response(
                {"error": response.get("error"), "details": response.get("message")},
                status=response_status
            )
            
            
            


















########################      PERKVILLE LOGIC      #############################
# from .Services.Perkville import PerkvilleOAuth, PerkvilleAPI
# Views for the Perkville OAuth flow
# class PerkvilleAuthView(APIView):
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         oauth_client = PerkvilleOAuth()
#         state = "random_state_here"  # You should generate this dynamically
        
#         # Define scopes based on your application needs
#         scopes = ["PUBLIC", "USER_CUSTOMER_INFO", "USER_REDEEM"]
        
#         # Get the authorization URL
#         auth_url = oauth_client.get_authorization_url(state=state, scopes=scopes)
        
#         # Redirect to Perkville's authorization page
#         return redirect(auth_url)

# class PerkvilleOAuthCallbackView(APIView):
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         """
#         Handle the OAuth callback from Perkville
#         """
#         # Get code and state from query parameters
#         code = request.GET.get('code')
#         state = request.GET.get('state')
        
#         if not code:
#             return Response(
#                 {"error": "No authorization code provided"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Exchange code for token
#         oauth_client = PerkvilleOAuth()
#         result = oauth_client.exchange_code_for_token(code, state)
        
#         if result.get("success"):
#             # Store token in session or return to client
#             # This depends on your application architecture
#             access_token = result["data"]["access_token"]
            
#             # You might want to store this token in your database or user session
#             # For example, you could update the user's profile in your database
            
#             return Response({
#                 "message": "Authentication successful",
#                 "token": access_token
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 "error": result.get("error"),
#                 "details": result.get("message")
#             }, status=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR))

# class PerkvillePasswordGrantView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         """
#         Get token using password grant (admin purposes only)
#         """
#         serializer = PasswordGrantSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
        
#         oauth_client = PerkvilleOAuth()
#         result = oauth_client.password_grant(username, password)
        
#         if result.get("success"):
#             access_token = result["data"]["access_token"]
            
#             return Response({
#                 "message": "Authentication successful",
#                 "token": access_token
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 "error": result.get("error"),
#                 "details": result.get("message")
#             }, status=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR))

# # Example of how to use the Perkville API client
# class PerkvilleUserInfoView(APIView):
#     def get(self, request):
#         """
#         Get user information from Perkville
#         """
#         # Get access token from request authentication or session
#         # This would depend on how you're storing the token
#         access_token = request.session.get('perkville_access_token')
        
#         if not access_token:
#             return Response(
#                 {"error": "No access token provided"},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
        
#         # Create API client
#         api_client = PerkvilleAPI(access_token)
        
#         # Make API request - for example, get user info
#         result = api_client.make_request('users/me')
        
#         if result.get("success"):
#             return Response(result["data"], status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 "error": result.get("error"),
#                 "details": result.get("message")
#             }, status=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR))

# from django.shortcuts import redirect
# from django.http import JsonResponse
# from django.conf import settings
# import requests

# # Step 1: Redirect the User to Perkville
# def redirect_to_perkville(request):
#     client_id = settings.PERKVILLE_CLIENT_ID
#     redirect_uri = settings.PERKVILLE_REDIRECT_URI
#     auth_url = settings.PERKVILLE_AUTH_URL
#     scope = "PUBLIC"

#     # Construct the authorization URL
#     url = f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
#     return redirect(url)

# # Step 2: Handle Perkville Callback and Receive Authorization Code
# def perkville_callback(request):
#     code = request.GET.get('code')
#     if not code:
#         return JsonResponse({"error": "Authorization code not provided."}, status=400)

#     # Step 3: Exchange Authorization Code for Access Token
#     token_url = settings.PERKVILLE_TOKEN_URL
#     client_id = settings.PERKVILLE_CLIENT_ID
#     client_secret = settings.PERKVILLE_CLIENT_SECRET
#     redirect_uri = settings.PERKVILLE_REDIRECT_URI

#     data = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "redirect_uri": redirect_uri,
#         "client_id": client_id,
#         "client_secret": client_secret
#     }

#     try:
#         response = requests.post(token_url, data=data)
#         if response.status_code == 200:
#             return JsonResponse(response.json(), status=200)
#         else:
#             return JsonResponse({"error": "Failed to exchange authorization code for access token.", "details": response.text}, status=response.status_code)
#     except Exception as e:
#         return JsonResponse({"error": "An error occurred while exchanging the authorization code.", "details": str(e)}, status=500)