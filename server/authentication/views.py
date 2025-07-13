from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import PasswordResetCode, EmailVerificationCode
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer
)
from .authentication import generate_jwt_token
from .utils import send_password_reset_email, send_email_verification_code
from settings.views import create_session_record
from settings.services import create_user_session

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                user = serializer.save()
                
                # Generate verification code
                verification_code = EmailVerificationCode.objects.create(user=user)
                
                # Send verification email
                try:
                    send_email_verification_code(user, verification_code)
                except Exception as e:
                    # Log error but don't fail registration
                    print(f"Failed to send verification email: {e}")
                
                # Generate JWT token
                token = generate_jwt_token(user)
                
                # Создать сессию
                session_key = request.session.session_key or request.session._get_or_create_session_key()
                ip_address = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                create_user_session(user, session_key, ip_address, user_agent)
                
                return Response({
                    'message': 'Registration successful',
                    'user': UserSerializer(user).data,
                    'token': token,
                    'session_key': session_key,
                    'verification_code_sent': True
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': 'Registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token = generate_jwt_token(user)
        
        # Создать сессию с JWT токеном
        session_key = request.session.session_key or request.session._get_or_create_session_key()
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        create_user_session(user, session_key, ip_address, user_agent, token)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'token': token,
            'session_key': session_key
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    try:
        # Получить session_key из заголовка X-Session-Key
        session_key = request.META.get('HTTP_X_SESSION_KEY')
        
        # Деактивировать текущую сессию
        if session_key:
            from settings.models import UserSession
            try:
                user_session = UserSession.objects.get(
                    session_key=session_key,
                    user=request.user,
                    is_active=True
                )
                user_session.is_active = False
                user_session.save()
            except UserSession.DoesNotExist:
                pass  # Сессия не найдена, это нормально
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Logout failed',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current user data"""
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset code"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Invalidate old reset codes
            PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Create new reset code
            reset_code = PasswordResetCode.objects.create(user=user)
            
            # Send reset email
            try:
                send_password_reset_email(user, reset_code)
                return Response({
                    'message': 'Password reset code sent to your email'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Failed to send reset email',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response({
                'message': 'If the email exists, a reset code has been sent'
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with code"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        reset_code = serializer.validated_data['reset_code']
        new_password = serializer.validated_data['new_password']
        
        try:
            with transaction.atomic():
                # Update password
                user.set_password(new_password)
                user.save()
                
                # Mark reset code as used
                reset_code.is_used = True
                reset_code.save()
                
                return Response({
                    'message': 'Password reset successful'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Password reset failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for authenticated user"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        try:
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Password change failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_email(request):
    """Verify email with code"""
    code = request.data.get('code')
    
    if not code:
        return Response({
            'error': 'Verification code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        verification_code = EmailVerificationCode.objects.filter(
            user=request.user,
            code=code,
            is_used=False
        ).first()
        
        if not verification_code:
            return Response({
                'error': 'Invalid verification code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if verification_code.is_expired():
            return Response({
                'error': 'Verification code has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Mark email as verified
            request.user.is_email_verified = True
            request.user.save()
            
            # Mark code as used
            verification_code.is_used = True
            verification_code.save()
            
            return Response({
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': 'Email verification failed',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification_code(request):
    """Resend email verification code"""
    if request.user.is_email_verified:
        return Response({
            'message': 'Email is already verified'
        }, status=status.HTTP_200_OK)
    
    try:
        # Invalidate old verification codes
        EmailVerificationCode.objects.filter(user=request.user, is_used=False).update(is_used=True)
        
        # Create new verification code
        verification_code = EmailVerificationCode.objects.create(user=request.user)
        
        # Send verification email
        send_email_verification_code(request.user, verification_code)
        
        return Response({
            'message': 'Verification code sent to your email'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to send verification code',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def user_update(request):
    """Update user data"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'User updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)