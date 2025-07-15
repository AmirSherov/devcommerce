import time
import hashlib
import hmac
from typing import Optional, Tuple
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .models import PublicAPIKey
from django.contrib.auth import get_user_model
from authentication.authentication import JWTAuthentication
User = get_user_model()


class PublicAPIAuthentication(authentication.BaseAuthentication):
    """
    🔑 АУТЕНТИФИКАЦИЯ ДЛЯ ПУБЛИЧНОГО API (JWT или X-API-KEY)
    """
    def authenticate(self, request: HttpRequest) -> Optional[Tuple[object, None]]:
        # 1. Если есть X-API-KEY — PublicAPIKey
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            try:
                public_api_key = PublicAPIKey.objects.select_related('container__user').get(
                    api_key=api_key,
                    is_active=True
                )
                can_request, message = public_api_key.can_make_request()
                if not can_request:
                    raise AuthenticationFailed(message)
                if not self._verify_signature(request, public_api_key):
                    raise AuthenticationFailed("Неверная подпись запроса")
                public_api_key.update_usage()
                return (public_api_key, None)
            except PublicAPIKey.DoesNotExist:
                raise AuthenticationFailed("Неверный API ключ")
            except Exception as e:
                raise AuthenticationFailed(f"Ошибка аутентификации: {str(e)}")
        # 2. Если есть JWT (Authorization: Bearer ...)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.lower().startswith('bearer '):
            jwt_auth = JWTAuthentication()
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple:
                user, _ = user_auth_tuple
                if user and user.is_authenticated:
                    return (user, None)
        return None
    
    def _verify_signature(self, request: HttpRequest, api_key: PublicAPIKey) -> bool:
        """Проверка подписи запроса"""
        signature = request.META.get('HTTP_X_SIGNATURE')
        if not signature:
            return True
        
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        if not timestamp:
            return False

        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - request_time) > 300:
                return False
        except ValueError:
            return False

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
        api_key = request.user
        user_plan = api_key.container.user.plan
        if user_plan == 'standard':
            return False
        
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
    elif hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
        container_id = request.GET.get('container_id')
        if container_id:
            try:
                from storage.models import StorageContainer
                container = StorageContainer.objects.get(id=container_id, user=request.user)
                return PublicAPIKey.objects.filter(container=container).first()
            except (StorageContainer.DoesNotExist, PublicAPIKey.DoesNotExist):
                pass
    return None


def log_api_request(request, response, api_key: PublicAPIKey, start_time: float):
    """Логирование API запроса"""
    from .models import PublicAPIRequest
    
    response_time = time.time() - start_time
    
    is_success = 200 <= response.status_code < 400
    error_message = ''
    error_code = ''
    
    if hasattr(response, 'data') and response.data:
        error_message = str(response.data.get('error', ''))
        error_code = str(response.data.get('error_code', ''))
    elif not is_success:
        error_message = f"HTTP {response.status_code}"
    
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
        error_message=error_message,
        error_code=error_code
    )
    update_daily_stats(api_key, is_success, response_time, request.path)


def update_daily_stats(api_key: PublicAPIKey, is_success: bool, response_time: float, endpoint: str):
    """Обновление ежедневной статистики"""
    import logging
    from .models import PublicAPIUsage
    
    logger = logging.getLogger(__name__)
    
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
    usage.total_response_time += response_time
    usage.average_response_time = usage.total_response_time / usage.total_requests
    endpoints = usage.popular_endpoints or {}
    endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
    usage.popular_endpoints = endpoints
    usage.save()