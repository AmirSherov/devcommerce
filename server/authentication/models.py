from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import string


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Премиум пользователь с расширенными возможностями")
    
    PLAN_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='standard',
        help_text="План подписки пользователя"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset code for {self.user.email}"


class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Verification code for {self.user.email}"
