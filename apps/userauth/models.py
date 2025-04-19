from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from .managers import CustomUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .signals import sendResetPasswordEmail


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('STAFF', 'Staff'),
        ('CLIENT', 'Client'),
    )
    username = models.CharField(
        max_length=150, 
        unique=True, 
        blank=True, 
        null=True
    )
    
    email = models.EmailField(
        _('email address'), 
        unique=True,
        error_messages={
            'unique': _("A user with this email already exists."),
        }
    )
    
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='CLIENT'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True, default=None)
    
    # OTP-related fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_secret_key = models.CharField(max_length=255, blank=True, null=True)
    otp_valid_until = models.DateTimeField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    State = models.CharField(max_length=50, blank=True, null=True)
    City = models.CharField(max_length=50, blank=True, null=True)
    Country = models.CharField(max_length=50, blank=True, null=True)
    PostalCode = models.CharField(max_length=10, blank=True, null=True)
    ReferredBy = models.CharField(max_length=50, blank=True, null=True)
    DateOfBirth = models.DateField(blank=True, null=True)
    IsMale = models.BooleanField(default=False)
    Gender_Types = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )
    Age = models.IntegerField(blank=True, null=True)
    Height = models.FloatField(blank=True, null=True)
    Weight = models.FloatField(blank=True, null=True)
    userRegDate = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    Gender = models.CharField(
        max_length=15, 
        choices=Gender_Types, 
        default='CLIENT',
        null=True
    )
    AddressLine1 = models.CharField(max_length=255, blank=True, null=True)

    mindbody_id = models.CharField(max_length=255, null=True, blank=True)  
    inbody_id = models.CharField(max_length=255, null=True, blank=True)
    
    is_staff_member = models.BooleanField(default=False)  
    
    
    perkville_access_token = models.CharField(max_length=255, blank=True, null=True)




    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email
    
    
    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
        sendResetPasswordEmail(reset_password_token)



from django.contrib.auth import get_user_model

User = get_user_model()

class PerkvilleProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perkville_profile')
    access_token = models.CharField(max_length=255, null=True, blank=True)
    token_created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_registered = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Perkville Profile - {self.user.username}"
    
class MindbodyClientProfile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mindbody_profile')
    # mindbody_id = models.CharField(max_length=255, null=True, blank=True)
    pass

class InbodyProfile(models.Model):
    pass