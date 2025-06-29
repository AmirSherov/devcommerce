import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import (
    AIGenerationRequest, AIGenerationStats, 
    AIPromptTemplate, GlobalAIStats
)
from .serializers import (
    AIGenerateRequestSerializer, AIGenerateResponseSerializer,
    AIGenerationRequestListSerializer, AIGenerationStatsSerializer,
    AIPromptTemplateSerializer, AIUserStatsSerializer,
    AILimitsSerializer, AIStyleStatsSerializer,
    AIGenerationRequestSerializer
)
from .services import sync_generate_portfolio
from .smart_generator import SmartAIGenerator

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_generate_portfolio(request):
    """Генерация портфолио через AI"""
    try:
        # Валидация входных данных
        serializer = AIGenerateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Ошибка валидации данных',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Подготавливаем данные для генерации
        validated_data = serializer.validated_data
        request_data = {
            'user': request.user,
            'title': validated_data['title'],
            'description': validated_data.get('description', ''),
            'prompt': validated_data['prompt'],
            'style': validated_data.get('style', 'modern'),
            'tags': validated_data.get('tags', [])
        }
        
        # Добавляем автоматические теги
        auto_tags = ['ai-generated', request_data['style']]
        request_data['tags'].extend(auto_tags)
        request_data['tags'] = list(set(request_data['tags']))  # Удаляем дубликаты
        
        # Запускаем генерацию
        result = sync_generate_portfolio(request_data)
        
        # Форматируем ответ
        response_serializer = AIGenerateResponseSerializer(result)
        
        if result['success']:
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Определяем HTTP статус по коду ошибки
            error_code = result.get('error_code', 'UNKNOWN')
            if error_code == 'LIMIT_EXCEEDED':
                http_status = status.HTTP_429_TOO_MANY_REQUESTS
            elif error_code == 'TIMEOUT':
                http_status = status.HTTP_408_REQUEST_TIMEOUT
            else:
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            return Response(response_serializer.data, status=http_status)
        
    except Exception as e:
        logger.error(f"Unexpected error in ai_generate_portfolio: {str(e)}")
        return Response({
            'success': False,
            'error': 'Внутренняя ошибка сервера',
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SmartAIGenerationView(APIView):
    """
    🚀 РЕВОЛЮЦИОННЫЙ AI ГЕНЕРАТОР САЙТОВ МИРОВОГО УРОВНЯ!
    
    Теперь с 7-шаговым процессом премиум генерации и автоматическими изображениями!
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Генерация сайта через ПРЕМИУМ AI процесс"""
        
        try:
            serializer = AIGenerationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            request_data = {
                'user': request.user,
                'prompt': serializer.validated_data['prompt'],
                'title': serializer.validated_data['title'],
                'description': serializer.validated_data.get('description', ''),
                'style': serializer.validated_data.get('style', 'modern'),
                'tags': serializer.validated_data.get('tags', []),
                'industry': serializer.validated_data.get('industry', 'general')
            }
            
            logger.info(f"🚀 [PREMIUM AI] Запрос РЕВОЛЮЦИОННОЙ генерации от {request.user.username}")
            
            # Создаем ПРЕМИУМ генератор и запускаем 7-шаговый процесс
            generator = SmartAIGenerator()
            result = generator.generate_website_premium(request_data)
            
            if result['success']:
                logger.info(f"🎉 [PREMIUM AI] ✅ ШЕДЕВР создан для {request.user.username}!")
                
                # Формируем расширенный ответ с информацией о премиум процессе
                response_data = {
                    'success': True,
                    'portfolio': {
                        'id': str(result['portfolio'].id),
                        'title': result['portfolio'].title,
                        'slug': result['portfolio'].slug,
                        'public_url': result['portfolio'].public_url,
                        'is_public': result['portfolio'].is_public,
                        'created_at': result['portfolio'].created_at.isoformat(),
                        'tags': result['portfolio'].tags
                    },
                    'generation_info': {
                        'request_id': result.get('request_id'),
                        'response_time': round(result.get('response_time', 0), 2),
                        'generation_steps': result.get('generation_steps', 7),
                        'enhanced_features': result.get('enhanced_features', []),
                        'process_type': 'premium_7_step'
                    },
                    'premium_features': {
                        'business_analysis': True,
                        'unique_design': True,
                        'professional_copy': True,
                        'auto_images': True,
                        'modern_interactions': True
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            else:
                logger.error(f"💥 [PREMIUM AI] ❌ Ошибка генерации: {result.get('error', 'Unknown error')}")
                
                return Response({
                    'success': False,
                    'error': result.get('error', 'Произошла ошибка при создании шедевра'),
                    'error_code': result.get('error_code', 'PREMIUM_ERROR')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"💥 [PREMIUM AI] ❌ Критическая ошибка: {str(e)}")
            
            return Response({
                'success': False,
                'error': 'Ошибка премиум генерации. Наши инженеры уже работают над исправлением!',
                'error_code': 'PREMIUM_CRITICAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PremiumAIGenerationWithProgressView(APIView):
    """
    🎯 ПРЕМИУМ ГЕНЕРАЦИЯ С ПОКАЗОМ ПРОГРЕССА
    
    WebSocket-like API для отслеживания прогресса 7-шагового процесса
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Запуск премиум генерации с детальным прогрессом"""
        
        try:
            # Валидация данных
            serializer = AIGenerationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Создаем кастомный генератор с callback'ами прогресса
            generator = ProgressTrackingGenerator(user=request.user)
            
            request_data = {
                'user': request.user,
                'prompt': serializer.validated_data['prompt'],
                'title': serializer.validated_data['title'],
                'description': serializer.validated_data.get('description', ''),
                'style': serializer.validated_data.get('style', 'modern'),
                'tags': serializer.validated_data.get('tags', []),
                'industry': serializer.validated_data.get('industry', 'general')
            }
            
            # Запускаем генерацию с трекингом прогресса
            result = generator.generate_with_progress(request_data)
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"💥 [PROGRESS AI] ❌ Ошибка: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка генерации с прогрессом'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgressTrackingGenerator:
    """Генератор с отслеживанием прогресса для frontend'а"""
    
    def __init__(self, user):
        self.user = user
        self.generator = SmartAIGenerator()
        self.progress_steps = [
            {"step": 1, "name": "🔍 Анализируем ваш бизнес", "description": "Изучаем индустрию и конкурентов"},
            {"step": 2, "name": "🏗️ Проектируем архитектуру", "description": "Создаём структуру и навигацию"},
            {"step": 3, "name": "🎨 Разрабатываем дизайн", "description": "Создаём уникальную концепцию"},
            {"step": 4, "name": "✍️ Пишем контент", "description": "Создаём продающие тексты"},
            {"step": 5, "name": "🖼️ Подбираем изображения", "description": "Интегрируем качественные фото"},
            {"step": 6, "name": "⚡ Добавляем интерактив", "description": "Создаём анимации и эффекты"},
            {"step": 7, "name": "🎯 Собираем шедевр", "description": "Финальная оптимизация и сборка"}
        ]
    
    def generate_with_progress(self, request_data):
        """Генерация с детальным прогрессом"""
        
        try:
            start_time = time.time()
            
            # Имитируем прогресс для демонстрации
            progress_data = {
                'success': True,
                'status': 'completed',
                'total_steps': 7,
                'completed_steps': 7,
                'current_step': {
                    'step': 7,
                    'name': '🎉 Готово!',
                    'description': 'Ваш сайт создан'
                },
                'steps_detail': self.progress_steps,
                'estimated_time': '45-60 секунд',
                'actual_time': 0
            }
            
            # Запускаем реальную генерацию
            result = self.generator.generate_website_premium(request_data)
            
            actual_time = round(time.time() - start_time, 2)
            progress_data['actual_time'] = actual_time
            
            if result['success']:
                progress_data.update({
                    'portfolio': {
                        'id': str(result['portfolio'].id),
                        'title': result['portfolio'].title,
                        'slug': result['portfolio'].slug,
                        'public_url': result['portfolio'].public_url,
                        'is_public': result['portfolio'].is_public,
                        'created_at': result['portfolio'].created_at.isoformat(),
                        'tags': result['portfolio'].tags
                    },
                    'generation_summary': {
                        'enhanced_features': result.get('enhanced_features', []),
                        'business_insights': f"Проанализирован бизнес типа '{request_data.get('industry', 'general')}'",
                        'design_uniqueness': "Создана уникальная дизайн-концепция",
                        'images_integrated': "Автоматически подобраны качественные изображения",
                        'code_quality': "Современный адаптивный код"
                    }
                })
            else:
                progress_data.update({
                    'success': False,
                    'error': result.get('error', 'Ошибка генерации'),
                    'status': 'failed'
                })
            
            return progress_data
            
        except Exception as e:
            logger.error(f"💥 [PROGRESS] Ошибка: {str(e)}")
            return {
                'success': False,
                'error': f'Ошибка в процессе генерации: {str(e)}',
                'status': 'failed'
            }


class GetUserLimitsView(APIView):
    """API для получения лимитов пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение информации о лимитах пользователя"""
        try:
            user = request.user
            today = timezone.now().date()
            
            # Получаем статистику за сегодня
            stats, created = AIGenerationStats.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'requests_count': 0,
                    'successful_count': 0,
                    'failed_count': 0
                }
            )
            
            # Настраиваем лимиты
            daily_limit = 5 if user.is_premium else 0
            used_today = stats.requests_count
            remaining_today = max(0, daily_limit - used_today)
            can_generate = user.is_premium and remaining_today > 0
            
            # Время сброса лимита
            tomorrow = today + timedelta(days=1)
            next_reset = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time()))
            
            # Формируем сообщение
            if not user.is_premium:
                limit_message = "AI генерация доступна только Premium пользователям"
            elif remaining_today == 0:
                limit_message = f"Исчерпан дневной лимит ({daily_limit}/день). Сбросится завтра."
            else:
                limit_message = f"Осталось {remaining_today} из {daily_limit} генераций на сегодня"
            
            return Response({
                'success': True,
                'data': {
                    'is_premium': user.is_premium,
                    'daily_limit': daily_limit,
                    'used_today': used_today,
                    'remaining_today': remaining_today,
                    'next_reset': next_reset.isoformat(),
                    'can_generate': can_generate,
                    'limit_message': limit_message
                }
            })
            
        except Exception as e:
            logger.error(f"[LIMITS] Ошибка получения лимитов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения лимитов пользователя'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIStatsView(APIView):
    """API для получения статистики AI"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение общей статистики AI"""
        try:
            user = request.user
            
            # Общие метрики пользователя
            total_requests = AIGenerationRequest.objects.filter(user=user).count()
            total_successful = AIGenerationRequest.objects.filter(user=user, status='success').count()
            total_failed = total_requests - total_successful
            
            success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
            
            # Среднее время ответа
            avg_response_time = AIGenerationRequest.objects.filter(
                user=user, 
                status='success', 
                response_time__isnull=False
            ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0
            
            # Любимый стиль
            favorite_style = AIGenerationRequest.objects.filter(user=user).values('style').annotate(
                count=Count('style')
            ).order_by('-count').first()
            
            return Response({
                'success': True,
                'data': {
                    'total_requests': total_requests,
                    'total_successful': total_successful,
                    'total_failed': total_failed,
                    'success_rate': round(success_rate, 1),
                    'average_response_time': round(avg_response_time, 2),
                    'favorite_style': favorite_style['style'] if favorite_style else 'modern'
                }
            })
            
        except Exception as e:
            logger.error(f"[STATS] Ошибка получения статистики: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения статистики'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIGenerationHistoryView(APIView):
    """API для получения истории AI генераций пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение истории генераций"""
        
        try:
            # Получаем последние 20 запросов пользователя
            requests = AIGenerationRequest.objects.filter(
                user=request.user
            ).select_related('portfolio_created').order_by('-created_at')[:20]
            
            history_data = []
            for req in requests:
                request_data = {
                    'id': req.id,
                    'title': req.title,
                    'prompt': req.prompt[:100] + '...' if len(req.prompt) > 100 else req.prompt,
                    'style': req.style,
                    'status': req.status,
                    'response_time': req.response_time,
                    'created_at': req.created_at.isoformat(),
                    'portfolio': None
                }
                
                if req.portfolio_created:
                    request_data['portfolio'] = {
                        'id': str(req.portfolio_created.id),
                        'slug': req.portfolio_created.slug,
                        'public_url': req.portfolio_created.public_url,
                        'is_public': req.portfolio_created.is_public
                    }
                
                history_data.append(request_data)
            
            return Response({
                'history': history_data,
                'total_requests': AIGenerationRequest.objects.filter(user=request.user).count()
            })
        
        except Exception as e:
            logger.error(f"[HISTORY] Ошибка получения истории: {str(e)}")
            
            return Response({
                'error': 'Ошибка получения истории'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PromptTemplatesView(APIView):
    """API для работы с шаблонами промптов"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение шаблонов промптов"""
        try:
            user = request.user
            
            # Получаем публичные шаблоны и шаблоны пользователя
            templates = AIPromptTemplate.objects.filter(
                Q(is_public=True) | Q(user=user)
            ).order_by('-is_featured', '-usage_count', '-created_at')
            
            # Фильтры
            category = request.GET.get('category')
            if category:
                templates = templates.filter(category=category)
            
            style = request.GET.get('style')
            if style:
                templates = templates.filter(style=style)
            
            serializer = AIPromptTemplateSerializer(templates, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка получения шаблонов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения шаблонов промптов'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Создание нового шаблона промпта"""
        try:
            user = request.user
            
            # Проверяем лимит шаблонов
            user_templates_count = AIPromptTemplate.objects.filter(user=user).count()
            if user_templates_count >= 20:
                return Response({
                    'success': False,
                    'error': 'Превышен лимит шаблонов (максимум 20)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = AIPromptTemplateSerializer(data=request.data)
            if serializer.is_valid():
                template = serializer.save(user=user)
                
                return Response({
                    'success': True,
                    'data': AIPromptTemplateSerializer(template).data,
                    'message': 'Шаблон успешно создан'
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'error': 'Некорректные данные',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка создания шаблона: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка создания шаблона'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 