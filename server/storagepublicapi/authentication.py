import time
import hashlib
import hmac
from typing import Optional, Tuple
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .models import PublicAPIKey


class PublicAPIAuthentication(authentication.BaseAuthentication):
    """
    🔑 АУТЕНТИФИКАЦИЯ ДЛЯ ПУБЛИЧНОГО API
    
    Проверяет API ключи и подписи запросов
    """
    
    def authenticate(self, request: HttpRequest) -> Optional[Tuple[PublicAPIKey, None]]:
        """Аутентификация по API ключу"""
        
        # Получаем API ключ из заголовка
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        try:
            # Находим API ключ
            public_api_key = PublicAPIKey.objects.select_related('container__user').get(
                api_key=api_key,
                is_active=True
            )
            
            # Проверяем возможность выполнения запроса
            can_request, message = public_api_key.can_make_request()
            if not can_request:
                raise AuthenticationFailed(message)
            
            # Проверяем подпись запроса (если есть)
            if not self._verify_signature(request, public_api_key):
                raise AuthenticationFailed("Неверная подпись запроса")
            
            # Обновляем статистику использования
            public_api_key.update_usage()
            
            return (public_api_key, None)
            
        except PublicAPIKey.DoesNotExist:
            raise AuthenticationFailed("Неверный API ключ")
        except Exception as e:
            raise AuthenticationFailed(f"Ошибка аутентификации: {str(e)}")
    
    def _verify_signature(self, request: HttpRequest, api_key: PublicAPIKey) -> bool:
        """Проверка подписи запроса"""
        
        # Получаем подпись из заголовка
        signature = request.META.get('HTTP_X_SIGNATURE')
        if not signature:
            return True  # Подпись необязательна для простых запросов
        
        # Получаем timestamp
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        if not timestamp:
            return False
        
        # Проверяем время запроса (не старше 5 минут)
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - request_time) > 300:  # 5 минут
                return False
        except ValueError:
            return False
        
        # Создаем подпись для проверки
        message = f"{request.method}{request.path}{timestamp}"
        expected_signature = hmac.new(
            api_key.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class PublicAPIPermission:
    """
    🔒 ПРОВЕРКА РАЗРЕШЕНИЙ ДЛЯ ПУБЛИЧНОГО API
    """
    
    def __init__(self, required_permissions: list = None):
        self.required_permissions = required_permissions or []
    
    def has_permission(self, request, view):
        """Проверка разрешений для API ключа"""
        
        api_key = request.user  # В нашем случае user = PublicAPIKey
        
        # Проверяем план пользователя
        user_plan = api_key.container.user.plan
        if user_plan == 'standard':
            return False  # Standard пользователи не имеют API доступа
        
        # Проверяем конкретные разрешения
        if self.required_permissions:
            api_permissions = api_key.permissions or {}
            for permission in self.required_permissions:
                if not api_permissions.get(permission, False):
                    return False
        
        return True


def get_api_key_from_request(request) -> Optional[PublicAPIKey]:
    """Получение API ключа из запроса"""
    if hasattr(request, 'user') and isinstance(request.user, PublicAPIKey):
        return request.user
    return None


def log_api_request(request, response, api_key: PublicAPIKey, start_time: float):
    """Логирование API запроса"""
    from .models import PublicAPIRequest
    
    # Вычисляем время ответа
    response_time = time.time() - start_time
    
    # Определяем статус
    is_success = 200 <= response.status_code < 400
    
    # Создаем запись о запросе
    PublicAPIRequest.objects.create(
        api_key=api_key,
        method=request.method,
        endpoint=request.path,
        status_code=response.status_code,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        ip_address=request.META.get('REMOTE_ADDR'),
        request_size=len(request.body) if request.body else 0,
        response_size=len(response.content) if hasattr(response, 'content') else 0,
        response_time=response_time,
        error_message='' if is_success else str(response.data.get('error', '')),
        error_code='' if is_success else str(response.data.get('error_code', ''))
    )
    
    # Обновляем ежедневную статистику
    update_daily_stats(api_key, is_success, response_time)


def update_daily_stats(api_key: PublicAPIKey, is_success: bool, response_time: float):
    """Обновление ежедневной статистики"""
    from .models import PublicAPIUsage
    
    today = timezone.now().date()
    
    usage, created = PublicAPIUsage.objects.get_or_create(
        api_key=api_key,
        date=today,
        defaults={
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'files_uploaded': 0,
            'files_downloaded': 0,
            'total_upload_size': 0,
            'total_download_size': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0,
            'popular_endpoints': {}
        }
    )
    
    # Обновляем счетчики
    usage.total_requests += 1
    if is_success:
        usage.successful_requests += 1
    else:
        usage.failed_requests += 1
    
    # Обновляем время ответа
    usage.total_response_time += response_time
    usage.average_response_time = usage.total_response_time / usage.total_requests
    
    # Обновляем популярные эндпоинты
    endpoints = usage.popular_endpoints or {}
    current_endpoint = f"{api_key.container.name}:{api_key.container.id}"
    endpoints[current_endpoint] = endpoints.get(current_endpoint, 0) + 1
    usage.popular_endpoints = endpoints
    
    usage.save() 