from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_password_reset_email(user, reset_code):
    """Send password reset email with code"""
    subject = 'Password Reset Code - DevCommerce'
    
    html_message = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Hello {user.first_name or user.username},</p>
        <p>You requested a password reset for your DevCommerce account.</p>
        <p>Your reset code is: <strong style="font-size: 24px; color: #007bff;">{reset_code.code}</strong></p>
        <p>This code will expire in 15 minutes.</p>
        <p>If you didn't request this reset, please ignore this email.</p>
        <br>
        <p>Best regards,<br>DevCommerce Team</p>
    </body>
    </html>
    """
    
    plain_message = f"""
    Password Reset Request
    
    Hello {user.first_name or user.username},
    
    You requested a password reset for your DevCommerce account.
    Your reset code is: {reset_code.code}
    
    This code will expire in 15 minutes.
    
    If you didn't request this reset, please ignore this email.
    
    Best regards,
    DevCommerce Team
    """
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_email_verification_code(user, verification_code):
    """Send email verification code"""
    subject = 'Email Verification Code - DevCommerce'
    
    html_message = f"""
    <html>
    <body>
        <h2>Email Verification</h2>
        <p>Hello {user.first_name or user.username},</p>
        <p>Thank you for registering with DevCommerce!</p>
        <p>Your verification code is: <strong style="font-size: 24px; color: #28a745;">{verification_code.code}</strong></p>
        <p>This code will expire in 15 minutes.</p>
        <p>Please use this code to verify your email address.</p>
        <br>
        <p>Welcome to DevCommerce!<br>DevCommerce Team</p>
    </body>
    </html>
    """
    
    plain_message = f"""
    Email Verification
    
    Hello {user.first_name or user.username},
    
    Thank you for registering with DevCommerce!
    Your verification code is: {verification_code.code}
    
    This code will expire in 15 minutes.
    Please use this code to verify your email address.
    
    Welcome to DevCommerce!
    DevCommerce Team
    """
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    ) 