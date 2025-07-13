from .models import UserSession
from django.utils import timezone
import hashlib

def get_token_hash(token):
    """Получить хеш токена"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_user_session(user, session_key, ip_address, user_agent, jwt_token=None):
    """Создать или обновить запись сессии пользователя"""
    session_record, created = UserSession.objects.get_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'is_active': True,
            'created_at': timezone.now(),
        }
    )
    
    if not created:
        # Обновить существующую запись
        session_record.last_activity = timezone.now()
        session_record.is_active = True
    
    # Сохранить хеш JWT токена если передан
    if jwt_token:
        session_record.jwt_token_hash = get_token_hash(jwt_token)
    
    session_record.save()
    session_record.make_trusted()
    return session_record 