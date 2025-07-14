import time
from django.utils.deprecation import MiddlewareMixin
from .authentication import get_api_key_from_request, log_api_request


class PublicAPILoggingMiddleware(MiddlewareMixin):
    """
    📝 MIDDLEWARE ДЛЯ ЛОГИРОВАНИЯ ПУБЛИЧНОГО API
    
    Автоматически логирует все API запросы
    """
    
    def process_request(self, request):
        """Обработка входящего запроса"""
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Обработка исходящего ответа"""
        
        # Проверяем, что это API запрос
        if request.path.startswith('/api/public/storage/'):
            api_key = get_api_key_from_request(request)
            if api_key:
                log_api_request(request, response, api_key, request.start_time)
        
        return response 