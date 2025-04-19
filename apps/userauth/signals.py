from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
import os 
from datetime import datetime
from django_rest_passwordreset.signals import reset_password_token_created
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



def sendResetPasswordEmail(reset_password_token):
    forgot_password_token = "{}".format(reset_password_token.key)
    greetings = "Hi {}!".format(reset_password_token.user.username)

    reset_password_url = "{}?token={}".format(os.getenv('FRONTEND_RESET_PASSWORD_URL'), forgot_password_token)
    email_html_content = "<html><body><p>{greetings}</p><p>Click the link below to reset your password:</p><p><a href='{reset_password_url}'>{reset_password_url}</a></p><p>If you did not request a password reset, please ignore this email.</p><p>Thanks,</p><p>Your Website Team</p></body></html>".format(
        greetings=greetings, reset_password_url=reset_password_url
    )
    message = Mail(
        from_email=os.getenv('EMAIL_SENDER'),
        to_emails=[reset_password_token.user.email],
        subject="Password Reset for {title}".format(title=os.getenv('WEBSITE_TITLE')),
        html_content=email_html_content,
    )
    sendgrid_client = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    response = sendgrid_client.send(message)

    if response.status_code == 202:
        print("Email sent successfully")
    else:
        print("Failed to send email")
        


# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
#     context = {
#         'current_user': reset_password_token.user,
#         'username': reset_password_token.user.username,
#         'email': reset_password_token.user.email,
#         'reset_password_url': "{}?token={}".format(
#             instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
#             reset_password_token.key)
#     }

#     email_html_message = render_to_string('email/password_reset_email.html', context)
#     email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

#     msg = EmailMultiAlternatives(
#         "Password Reset for Your Website",
#         email_plaintext_message,
#         "noreply@yourwebsite.com",
#         [reset_password_token.user.email]
#     )
#     msg.attach_alternative(email_html_message, "text/html")
#     msg.send()