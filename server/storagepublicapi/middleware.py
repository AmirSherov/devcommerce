import time
import logging
from django.utils.deprecation import MiddlewareMixin
from .authentication import get_api_key_from_request, log_api_request

logger = logging.getLogger(__name__)


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
        if request.path.startswith('/api/remote/storage/'):
            is_external = self._is_external_api_request(request)
            logger.debug(f"[MIDDLEWARE] Проверяем запрос: {request.path} - внешний: {is_external}")
            
            if is_external:
                logger.info(f"[MIDDLEWARE] Обрабатываем ВНЕШНИЙ API запрос: {request.path}")
                api_key = get_api_key_from_request(request)
                if api_key:
                    logger.info(f"[MIDDLEWARE] Найден API ключ: {str(api_key.api_key)[:10]}...")
                    log_api_request(request, response, api_key, request.start_time)
                else:
                    logger.warning(f"[MIDDLEWARE] API ключ не найден для запроса: {request.path}")
            else:
                logger.debug(f"[MIDDLEWARE] Игнорируем внутренний запрос: {request.path}")
        
        return response
    
    def _is_external_api_request(self, request):
        """Проверяет, является ли запрос внешним API запросом"""
        if request.path.endswith('/stats/') or request.path.endswith('/keys/'):
            logger.debug(f"[MIDDLEWARE] Внутренний запрос (статистика/ключи): {request.path}")
            return False
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge']):
            logger.debug(f"[MIDDLEWARE] Внутренний запрос (браузер): {request.path} - UA: {user_agent[:50]}")
            return False
        referer = request.META.get('HTTP_REFERER', '')
        if referer and any(domain in referer.lower() for domain in ['localhost', '127.0.0.1', 'devcommerce.com']):
            logger.debug(f"[MIDDLEWARE] Внутренний запрос (referer): {request.path} - Referer: {referer}")
            return False
        origin = request.META.get('HTTP_ORIGIN', '')
        if origin and any(domain in origin.lower() for domain in ['localhost', '127.0.0.1', 'devcommerce.com']):
            return False
        
        if request.META.get('HTTP_X_API_KEY'):
            return True
        return True 