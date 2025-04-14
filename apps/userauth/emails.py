import pyotp
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User

def send_otp_via_email(email, request=None):
   
    secret_key = pyotp.random_base32()

    totp = pyotp.TOTP(secret_key, interval=30)
    
    otp = totp.now()
    valid_date = timezone.now() + timedelta(minutes=10)
    
    if request:
        request.session['otp_secret_key'] = secret_key
        request.session['otp_valid_date'] = valid_date.isoformat()
    
    subject = 'Your Verification Code'
    message = f'Your verification code is {otp}. This code will expire in 10 minutes.'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    
    try:
        user_obj = User.objects.get(email=email)
        user_obj.otp_secret_key = secret_key
        user_obj.otp_valid_until = valid_date
        user_obj.save()
    except User.DoesNotExist:
        pass
    
    return otp

