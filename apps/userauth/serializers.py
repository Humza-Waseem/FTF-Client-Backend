from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from allauth.socialaccount.models import SocialAccount
# from django.contrib.auth.password_validation import validate_password
from .emails import *


User = get_user_model()

#The User Registration Serializer
# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(
#         write_only=True, 
#         required=True, 
#         style={'input_type': 'password'}
#     )

#     class Meta:
#         model = User
#         fields = (
#             'first_name', 
#             'last_name', 
#             'email', 
#             'phone_number', 
#             'password',  
#             'State', 
#             'City', 
#             'PostalCode', 
#             'AddressLine1', 
#             'Gender', 
#             'DateOfBirth', 
#             'Country'
#         )
#         extra_kwargs = {
#             'first_name': {'required': False},
#             'last_name': {'required': False},
#             'email': {'required': True},
#             'password': {'write_only': True}
#         }
    
#     def validate_email(self, value):        
#         try:
#             validate_email(value) 
#         except DjangoValidationError:
#             raise serializers.ValidationError("This doesn't look like an email, ex: name@domain.com") #if the eMail is not in a correct format
#         return value
    
#     def validate(self, data):
#         if len(data['password']) < 8:
#             raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})

#         email = data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError({"email": "A user with this email already exists."})
        

#         return data

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             email=validated_data['email'],
#             password=validated_data['password'],
#             first_name=validated_data.get('first_name', ''),
#             last_name=validated_data.get('last_name', ''),
#             phone_number=validated_data.get('phone_number', ''),
            
#             State=validated_data.get('State', ''),
#             City=validated_data.get('City', ''),
#             PostalCode=validated_data.get('PostalCode', ''),
#             Country=validated_data.get('Country', ''),
#             Gender= validated_data.get('Gender', ''),
#             DateOfBirth=validated_data.get('DateOfBirth', ''),

#             AddressLine1=validated_data.get('AddressLine1', ''),
            
      
                
#         )
#         return user






class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    DateOfBirth = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d", "iso-8601"])

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'State',
            'City',
            'PostalCode',
            'AddressLine1',
            'Gender',
            'DateOfBirth',
            'Country',
            'Age',
            'Height',
            'Weight',
            'userRegDate',
            'mindbody_id',
            'inbody_id',
            
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "mindbody_id": {"read_only": True},
            "inbody_id": {"read_only": True},
            "user_type": {"read_only": True},
            "is_staff": {"read_only": True},
            
        }
    
    def validate_email(self, value):
        try:
            validate_email(value)            
        except DjangoValidationError:
            raise serializers.ValidationError("This doesn't look like an email, ex: name@domain.com") #if the eMail is not in a correct format        
        return value
    def validate(self, attrs):
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        

        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        # Validate password strength
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs
        



    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            State=validated_data.get('State', ''),
            City=validated_data.get('City', ''),
            PostalCode=validated_data.get('PostalCode', ''),
            Country=validated_data.get('Country', ''),
            Gender=validated_data.get('Gender', ''),
            DateOfBirth=validated_data.get('DateOfBirth', ''),
            AddressLine1=validated_data.get('AddressLine1', ''),
            Age=validated_data.get('Age', ''),
            Height=validated_data.get('Height', ''),
            Weight = validated_data.get('Weight', ''),
            userRegDate=validated_data.get('userRegDate', ''),
            mindbody_id=validated_data.get('mindbody_id', ''),
            inbody_id=validated_data.get('inbody_id', ''),
            
        )
        return user







        
#The User Login Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            refresh = self.get_token(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type
                }
            }

            return data

        raise serializers.ValidationError("Must include 'email' and 'password'")

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        token['email'] = user.email

        return token
    
    
##################   OTP SERIALIZERS  #####################
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No user found with this email."})
        if len(otp) != 6:
            raise serializers.ValidationError({"otp": "OTP must be a 6-digit number."})

        return data
            
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)
    
    
    
    
    
    

##################    SOCIALS LOGIN #######################
# class SocialLoginSerializer(serializers.Serializer):
#     access_token = serializers.CharField(required=True)

#     def validate_access_token(self, access_token):
#         # You can add additional token validation if needed
#         return access_token

#     def create(self, validated_data):
#         # This method will be called to create or get the user
#         access_token = validated_data['access_token']
        
#         try:
#             # Use allauth's social login process
#             from allauth.socialaccount.helpers import complete_social_login
#             from allauth.socialaccount.models import SocialApp
#             from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
            
#             # Get the Google social app
#             social_app = SocialApp.objects.get(provider='google')
            
#             # Perform the social login
#             from allauth.socialaccount.helpers import complete_social_login
#             from allauth.socialaccount.providers.oauth2.client import OAuth2Client
            
#             client = OAuth2Client(access_token=access_token)
            
#         except Exception as e:
#             raise serializers.ValidationError(f"Invalid token: {str(e)}")

#         # Get or create the user
#         social_account = SocialAccount.objects.filter(
#             uid=social_account.uid, 
#             provider='google'
#         ).first()

#         if social_account:
#             user = social_account.user
#         else:
#             # Create a new user if not exists
#             email = social_account.extra_data.get('email')
#             first_name = social_account.extra_data.get('given_name', '')
#             last_name = social_account.extra_data.get('family_name', '')
            
#             user = User.objects.create_user(
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name,
#                 username=email  # Optional: you might want to generate a unique username
#             )

#         return user       
        
        
        
###### PASSWORD RESET LOGIC
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if the email exists in the system
        users = User.objects.filter(email=value)
        if not users.exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value
class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        # Validate passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Decode the UID and get the user
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError("Invalid user identifier.")

        # Validate the token
        if not default_token_generator.check_token(user, data['token']):
            raise ValidationError("Invalid or expired token.")

        return data

    def save(self):
        # Decode the UID and get the user
        uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = User.objects.get(pk=uid)
        
        # Set the new password
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
    
# Password Reset Serializer
# class PasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

#     def validate(self, data):
#         # Validate that passwords match
#         if data['new_password'] != data['confirm_password']:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
#         # Password strength validation
#         if len(data['new_password']) < 8:
#             raise serializers.ValidationError({"new_password": "Password must be at least 8 characters long."})
        
#         return data

#     def create(self, validated_data):
#         # Find user by email
#         try:
#             user = User.objects.get(email=validated_data['email'])
#         except User.DoesNotExist:
#             raise serializers.ValidationError({"email": "No user found with this email."})
        
#         # Set new password
#         user.set_password(validated_data['new_password'])
#         user.save()
        
#         return user   
        
        

    

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['user_type'] = user.user_type
#         return token