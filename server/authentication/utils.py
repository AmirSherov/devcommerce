from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_password_reset_email(user, reset_code):
    """Send password reset email using HTML template"""
    subject = 'Сброс пароля - DevCommerce'
    
    # Render HTML template
    context = {
        'user': user,
        'reset_code': reset_code,
    }
    
    html_message = render_to_string('emails/password_reset.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_email_verification_code(user, verification_code):
    """Send email verification code using HTML template"""
    subject = 'Подтверждение почты - DevCommerce'
    
    # Render HTML template
    context = {
        'user': user,
        'verification_code': verification_code,
    }
    
    html_message = render_to_string('emails/email_verification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    ) 