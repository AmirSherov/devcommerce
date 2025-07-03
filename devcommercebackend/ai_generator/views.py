import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from portfolio_templates.models import PortfolioTemplate
from portfolio.models import Portfolio
from .models import (
    TemplateAIGeneration, TemplateAIStats, 
    GlobalTemplateAIStats
)
from .serializers import (
    TemplateAIGenerationSerializer,
    TemplateAIStatsSerializer,
    TemplateAIGenerationRequestSerializer
)
from .services import TemplateAIService

logger = logging.getLogger(__name__)
User = get_user_model()


class TemplateAIGenerateView(APIView):
    """
    🤖 API ДЛЯ AI ЗАПОЛНЕНИЯ ШАБЛОНОВ
    
    POST /api/ai-generator/templates/{template_id}/generate/ - AI заполнение шаблона
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, template_id):
        """AI заполнение шаблона пользовательскими данными"""
        
        try:
            # Проверяем что пользователь премиум
            if not request.user.is_premium:
                return Response({
                    'success': False,
                    'error': 'AI заполнение шаблонов доступно только Premium пользователям',
                    'error_code': 'PREMIUM_REQUIRED'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Проверяем лимиты пользователя
            can_generate, limit_message = self._check_user_limits(request.user)
            if not can_generate:
                return Response({
                    'success': False,
                    'error': limit_message,
                    'error_code': 'LIMIT_EXCEEDED'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Получаем шаблон
            template = get_object_or_404(
                PortfolioTemplate, 
                id=template_id, 
                is_active=True
            )
            
            # Проверяем премиум шаблон
            if template.is_premium and not request.user.is_premium:
                return Response({
                    'success': False,
                    'error': 'Премиум шаблон доступен только Premium пользователям',
                    'error_code': 'PREMIUM_TEMPLATE_REQUIRED'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Валидируем данные запроса
            serializer = TemplateAIGenerationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            logger.info(f"🤖 [AI TEMPLATE] Запрос от {request.user.username} для шаблона '{template.title}'")
            
            # Создаем запись о генерации
            ai_generation = TemplateAIGeneration.objects.create(
                user=request.user,
                template=template,
                project_title=validated_data['project_title'],
                project_description=validated_data['project_description'],
                user_data=validated_data['user_data'],
                original_html=template.html_code,
                status='processing'
            )
            
            # Запускаем AI сервис (асинхронно)
            ai_service = TemplateAIService()
            result = ai_service.generate_personalized_template(
                template=template,
                user_data=validated_data['user_data'],
                project_title=validated_data['project_title'],
                project_description=validated_data['project_description'],
                user=request.user,
                ai_generation=ai_generation
            )
            
            if result['success']:
                # Обновляем статистику
                self._update_user_stats(request.user, 'ai_success')
                self._update_template_stats(template, 'ai_success')
                
                logger.info(f"✅ [AI TEMPLATE] Успешная генерация для {request.user.username}")
                
                return Response({
                    'success': True,
                    'portfolio': {
                        'id': str(result['portfolio'].id),
                        'title': result['portfolio'].title,
                        'slug': result['portfolio'].slug,
                        'edit_url': f'/portfolio/edit/me?project={result["portfolio"].id}',
                        'public_url': result['portfolio'].public_url if result['portfolio'].is_public else None
                    },
                    'generation_info': {
                        'generation_id': ai_generation.id,
                        'response_time': result.get('response_time', 0),
                        'template_used': template.title,
                        'ai_enhanced': True
                    },
                    'message': 'Шаблон успешно заполнен AI и портфолио создано'
                }, status=status.HTTP_201_CREATED)
            
            else:
                # Обновляем статистику ошибок
                self._update_user_stats(request.user, 'ai_failed')
                self._update_template_stats(template, 'ai_failed')
                
                logger.error(f"❌ [AI TEMPLATE] Ошибка генерации: {result.get('error', 'Unknown error')}")
                
                return Response({
                    'success': False,
                    'error': 'В данный момент серверы перегружены, попробуйте позже',
                    'error_code': 'SERVER_OVERLOAD',
                    'generation_id': ai_generation.id
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"💥 [AI TEMPLATE] Критическая ошибка: {str(e)}")
            
            return Response({
                'success': False,
                'error': 'Внутренняя ошибка сервера',
                'error_code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_user_limits(self, user: User) -> tuple[bool, str]:
        """Проверка лимитов пользователя (10 AI генераций в день)"""
        today = timezone.now().date()
        
        stats, created = TemplateAIStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'ai_requests_count': 0,
                'ai_successful_count': 0,
                'ai_failed_count': 0,
                'regular_usage_count': 0
            }
        )
        
        daily_limit = 10  # Строгий лимит для премиум пользователей
        used_today = stats.ai_requests_count
        remaining = max(0, daily_limit - used_today)
        
        if remaining <= 0:
            return False, f"Превышен дневной лимит AI генераций ({daily_limit}/день). Попробуйте завтра."
        
        return True, f"Осталось {remaining} из {daily_limit} AI генераций на сегодня"
    
    def _update_user_stats(self, user: User, result_type: str):
        """Обновление статистики пользователя"""
        today = timezone.now().date()
        
        stats, created = TemplateAIStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'ai_requests_count': 0,
                'ai_successful_count': 0,
                'ai_failed_count': 0,
                'regular_usage_count': 0
            }
        )
        
        stats.ai_requests_count += 1
        
        if result_type == 'ai_success':
            stats.ai_successful_count += 1
        elif result_type == 'ai_failed':
            stats.ai_failed_count += 1
        
        stats.save()
    
    def _update_template_stats(self, template: PortfolioTemplate, result_type: str):
        """Обновление статистики шаблона"""
        # Обновляем счетчик использований шаблона
        if result_type == 'ai_success':
            template.increment_uses()


class GetUserAILimitsView(APIView):
    """
    📊 API ДЛЯ ПОЛУЧЕНИЯ ЛИМИТОВ AI ГЕНЕРАЦИЙ
    
    GET /api/ai-generator/limits/ - информация о лимитах пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение информации о лимитах AI генераций"""
        try:
            user = request.user
            today = timezone.now().date()
            
            # Получаем статистику за сегодня
            stats, created = TemplateAIStats.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'ai_requests_count': 0,
                    'ai_successful_count': 0,
                    'ai_failed_count': 0,
                    'regular_usage_count': 0
                }
            )
            
            # Настраиваем лимиты
            daily_limit = 10 if user.is_premium else 0
            used_today = stats.ai_requests_count
            remaining_today = max(0, daily_limit - used_today)
            can_generate = user.is_premium and remaining_today > 0
            
            # Время сброса лимита
            tomorrow = today + timedelta(days=1)
            next_reset = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time()))
            
            # Формируем сообщение
            if not user.is_premium:
                limit_message = "AI заполнение шаблонов доступно только Premium пользователям"
            elif remaining_today == 0:
                limit_message = f"Исчерпан дневной лимит ({daily_limit}/день). Сбросится завтра."
            else:
                limit_message = f"Осталось {remaining_today} из {daily_limit} AI генераций на сегодня"
            
            return Response({
                'success': True,
                'data': {
                    'is_premium': user.is_premium,
                    'daily_limit': daily_limit,
                    'used_today': used_today,
                    'remaining_today': remaining_today,
                    'next_reset': next_reset.isoformat(),
                    'can_generate': can_generate,
                    'limit_message': limit_message,
                    'regular_usage_today': stats.regular_usage_count,
                    'total_usage_today': stats.total_usage
                }
            })
            
        except Exception as e:
            logger.error(f"[AI LIMITS] Ошибка получения лимитов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения лимитов пользователя'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateAIStatsView(APIView):
    """
    📈 API ДЛЯ СТАТИСТИКИ AI ГЕНЕРАЦИЙ
    
    GET /api/ai-generator/stats/ - статистика AI использования
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение статистики AI генераций пользователя"""
        try:
            user = request.user
            
            # Общие метрики пользователя
            total_ai_requests = TemplateAIGeneration.objects.filter(user=user).count()
            total_ai_successful = TemplateAIGeneration.objects.filter(user=user, status='success').count()
            total_ai_failed = total_ai_requests - total_ai_successful
            
            ai_success_rate = (total_ai_successful / total_ai_requests * 100) if total_ai_requests > 0 else 0
            
            # Среднее время ответа AI
            avg_ai_response_time = TemplateAIGeneration.objects.filter(
                user=user, 
                status='success', 
                response_time__isnull=False
            ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0
            
            # Популярные шаблоны пользователя
            popular_templates = TemplateAIGeneration.objects.filter(user=user).values(
                'template__title'
            ).annotate(
                count=Count('template')
            ).order_by('-count')[:5]
            
            # Статистика за последние 7 дней
            last_week_stats = TemplateAIStats.objects.filter(
                user=user,
                date__gte=timezone.now().date() - timedelta(days=7)
            ).aggregate(
                total_ai=Sum('ai_requests_count'),
                total_regular=Sum('regular_usage_count')
            )
            
            return Response({
                'success': True,
                'data': {
                    'total_ai_requests': total_ai_requests,
                    'total_ai_successful': total_ai_successful,
                    'total_ai_failed': total_ai_failed,
                    'ai_success_rate': round(ai_success_rate, 1),
                    'average_ai_response_time': round(avg_ai_response_time, 2),
                    'popular_templates': popular_templates,
                    'last_week': {
                        'ai_requests': last_week_stats['total_ai'] or 0,
                        'regular_usage': last_week_stats['total_regular'] or 0
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"[AI STATS] Ошибка получения статистики: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения статистики'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateAIHistoryView(APIView):
    """
    📚 API ДЛЯ ИСТОРИИ AI ГЕНЕРАЦИЙ
    
    GET /api/ai-generator/history/ - история AI генераций пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение истории AI генераций"""
        
        try:
            # Получаем последние 20 AI генераций пользователя
            generations = TemplateAIGeneration.objects.filter(
                user=request.user
            ).select_related('template', 'portfolio_created').order_by('-created_at')[:20]
            
            history_data = []
            for gen in generations:
                generation_data = {
                    'id': gen.id,
                    'project_title': gen.project_title,
                    'template': {
                        'id': gen.template.id,
                        'title': gen.template.title,
                        'category': gen.template.category
                    },
                    'status': gen.status,
                    'response_time': gen.response_time,
                    'created_at': gen.created_at.isoformat(),
                    'portfolio': None
                }
                
                if gen.portfolio_created:
                    generation_data['portfolio'] = {
                        'id': str(gen.portfolio_created.id),
                        'slug': gen.portfolio_created.slug,
                        'edit_url': f'/portfolio/edit/me?project={gen.portfolio_created.id}',
                        'public_url': gen.portfolio_created.public_url,
                        'is_public': gen.portfolio_created.is_public
                    }
                
                history_data.append(generation_data)
            
            return Response({
                'success': True,
                'history': history_data,
                'total_generations': TemplateAIGeneration.objects.filter(user=request.user).count()
            })
        
        except Exception as e:
            logger.error(f"[AI HISTORY] Ошибка получения истории: {str(e)}")
            
            return Response({
                'success': False,
                'error': 'Ошибка получения истории'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Функция для обновления статистики обычного использования шаблонов
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_regular_template_usage(request):
    """
    📊 ОТСЛЕЖИВАНИЕ ОБЫЧНОГО ИСПОЛЬЗОВАНИЯ ШАБЛОНОВ
    
    POST /api/ai-generator/track-regular-usage/ - учет обычного использования
    """
    try:
        user = request.user
        today = timezone.now().date()
        
        # Обновляем статистику обычного использования
        stats, created = TemplateAIStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'ai_requests_count': 0,
                'ai_successful_count': 0,
                'ai_failed_count': 0,
                'regular_usage_count': 0
            }
        )
        
        stats.regular_usage_count += 1
        stats.save()
        
        logger.info(f"📊 [REGULAR USAGE] Учтено обычное использование для {user.username}")
        
        return Response({
            'success': True,
            'message': 'Статистика обновлена'
        })
        
    except Exception as e:
        logger.error(f"[REGULAR USAGE] Ошибка: {str(e)}")
        return Response({
            'success': False,
            'error': 'Ошибка обновления статистики'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
