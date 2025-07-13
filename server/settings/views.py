from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from .models import UserProfile, UserNotificationSettings, UserSession
from .serializers import (
    UserProfileSerializer, UserNotificationSettingsSerializer, 
    UserSessionSerializer, ChangePasswordSerializer, AvatarUploadSerializer
)
from .models import cleanup_expired_sessions

User = get_user_model()


def is_session_trusted(request):
    """Проверить, может ли текущая сессия управлять другими сессиями"""
    session_key = request.META.get('HTTP_X_SESSION_KEY') or getattr(request.session, 'session_key', None)
    try:
        current_session = UserSession.objects.get(
            session_key=session_key,
            user=request.user,
            is_active=True
        )
        return current_session.can_manage_sessions
    except UserSession.DoesNotExist:
        return False


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_settings(request):
    """Получить или обновить настройки профиля"""
    
    # Получить или создать профиль
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response({
            'profile': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Профиль успешно обновлен',
                'profile': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """Загрузить аватар пользователя"""
    
    serializer = AvatarUploadSerializer(data=request.FILES)
    if serializer.is_valid():
        try:
            # Получить или создать профиль
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Удалить старый аватар если есть
            if profile.avatar:
                if default_storage.exists(profile.avatar.name):
                    default_storage.delete(profile.avatar.name)
            
            # Сохранить новый аватар
            avatar_file = serializer.validated_data['avatar']
            file_name = f"avatars/{request.user.id}_{int(timezone.now().timestamp())}_{avatar_file.name}"
            
            profile.avatar.save(file_name, avatar_file, save=True)
            
            return Response({
                'message': 'Аватар успешно загружен',
                'avatar_url': profile.avatar.url
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Ошибка при загрузке аватара'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    """Получить или обновить настройки уведомлений"""
    
    # Получить или создать настройки уведомлений
    settings, created = UserNotificationSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserNotificationSettingsSerializer(settings)
        return Response({
            'notification_settings': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UserNotificationSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Настройки уведомлений обновлены',
                'notification_settings': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_sessions(request):
    """Получить активные сессии пользователя"""
    
    # Очистить истекшие сессии
    cleanup_expired_sessions()
    
    # Получить все сессии пользователя
    sessions = UserSession.objects.filter(user=request.user, is_active=True)
    serializer = UserSessionSerializer(sessions, many=True, context={'request': request})
    sessions_data = serializer.data

    # Найти текущую сессию
    current_session = None
    for s in sessions_data:
        if s.get('is_current_session'):
            current_session = s
            break
    can_manage = current_session['can_manage_sessions'] if current_session else False

    return Response({
        'sessions': sessions_data,
        'total_sessions': sessions.count(),
        'retention_period_days': 15,
        'can_manage_sessions': can_manage,
        'session_trust_required_days': 3
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def terminate_session(request, session_id):
    """Завершить конкретную сессию"""
    
    # Проверить права на управление сессиями
    if not is_session_trusted(request):
        return Response({
            'error': 'Для управления сессиями необходимо использовать сайт минимум 3 дня с этого устройства'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        session = UserSession.objects.get(
            id=session_id, 
            user=request.user, 
            is_active=True
        )
        
        # Нельзя завершить текущую сессию
        if session.session_key == request.session.session_key:
            return Response({
                'error': 'Нельзя завершить текущую сессию'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Просто деактивировать сессию
        session.is_active = False
        session.save()
        
        return Response({
            'message': 'Сессия успешно завершена',
            'session_terminated': True
        }, status=status.HTTP_200_OK)
        
    except UserSession.DoesNotExist:
        return Response({
            'error': 'Сессия не найдена'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def terminate_all_sessions(request):
    """Завершить все сессии кроме текущей"""
    
    # Проверить права на управление сессиями
    if not is_session_trusted(request):
        return Response({
            'error': 'Для управления сессиями необходимо использовать сайт минимум 3 дня с этого устройства'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Получить session_key из заголовка или из сессии
    current_session_key = request.META.get('HTTP_X_SESSION_KEY') or getattr(request.session, 'session_key', None)
    
    # Получить все сессии для завершения
    sessions_to_terminate = UserSession.objects.filter(
        user=request.user, 
        is_active=True
    ).exclude(session_key=current_session_key)
    
    # Просто деактивировать сессии
    terminated_count = sessions_to_terminate.update(is_active=False)
    
    return Response({
        'message': f'Завершено {terminated_count} сессий',
        'terminated_count': terminated_count,
        'sessions_terminated': True
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Сменить пароль пользователя"""
    
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Сменить пароль
                user = request.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # Завершить все сессии кроме текущей
                UserSession.objects.filter(
                    user=user, 
                    is_active=True
                ).exclude(
                    session_key=request.session.session_key
                ).update(is_active=False)
                
                return Response({
                    'message': 'Пароль успешно изменен. Все другие сессии завершены.',
                    'password_changed': True
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Ошибка при смене пароля'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session_record(request):
    """Создать запись о новой сессии (вызывается при входе)"""
    
    session_key = request.session.session_key
    if not session_key:
        return Response({
            'error': 'Сессия не найдена'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Получить IP адрес
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # Создать или обновить запись сессии
    session_record, created = UserSession.objects.get_or_create(
        session_key=session_key,
        defaults={
            'user': request.user,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'is_active': True
        }
    )
    
    if not created:
        # Обновить существующую запись
        session_record.last_activity = timezone.now()
        session_record.is_active = True
        session_record.save()
    
    # Проверить, можно ли сделать сессию доверенной
    session_record.make_trusted()
    
    return Response({
        'message': 'Сессия зарегистрирована',
        'session_trusted': session_record.session_trusted,
        'can_manage_sessions': session_record.can_manage_sessions
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def settings_overview(request):
    """Получить обзор всех настроек пользователя"""
    
    # Получить профиль
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile_serializer = UserProfileSerializer(profile)
    
    # Получить настройки уведомлений
    notification_settings, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
    notification_serializer = UserNotificationSettingsSerializer(notification_settings)
    
    # Получить количество активных сессий
    active_sessions_count = UserSession.objects.filter(
        user=request.user, 
        is_active=True
    ).count()
    
    # Проверить права на управление сессиями
    can_manage_sessions = is_session_trusted(request)
    
    return Response({
        'profile': profile_serializer.data,
        'notification_settings': notification_serializer.data,
        'active_sessions_count': active_sessions_count,
        'is_premium': request.user.is_premium,
        'can_manage_sessions': can_manage_sessions
    }, status=status.HTTP_200_OK) 