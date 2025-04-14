from django.core.mail import send_mail
from django.conf import settings

def test_email():
    subject = "Test Email"
    message = "This is a test email from Django."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['hamza.wasym99@gmail.com'] 

    try:
        send_mail(subject, message, email_from, recipient_list)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")