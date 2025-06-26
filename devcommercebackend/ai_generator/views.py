from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Sum, Q
from datetime import datetime, timedelta
import logging

from .models import (
    AIGenerationRequest, AIGenerationStats, 
    AIPromptTemplate, GlobalAIStats
)
from .serializers import (
    AIGenerateRequestSerializer, AIGenerateResponseSerializer,
    AIGenerationRequestListSerializer, AIGenerationStatsSerializer,
    AIPromptTemplateSerializer, AIUserStatsSerializer,
    AILimitsSerializer, AIStyleStatsSerializer
)
from .services import sync_generate_portfolio

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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_generation_limits(request):
    """Получение информации о лимитах пользователя"""
    try:
        user = request.user
        today = timezone.now().date()
        stats, created = AIGenerationStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'requests_count': 0,
                'successful_count': 0,
                'failed_count': 0
            }
        )
        
        # Подготавливаем данные о лимитах
        daily_limit = 5 if user.is_premium else 0
        used_today = stats.requests_count
        remaining_today = max(0, daily_limit - used_today)
        can_generate = user.is_premium and remaining_today > 0
        
        # Время сброса лимита (00:00 следующего дня)
        tomorrow = today + timedelta(days=1)
        next_reset = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time()))
        
        # Сообщение о лимите
        if not user.is_premium:
            limit_message = "AI генерация доступна только Premium пользователям"
        elif remaining_today == 0:
            limit_message = f"Исчерпан дневной лимит ({daily_limit}/день). Сбросится завтра."
        else:
            limit_message = f"Осталось {remaining_today} из {daily_limit} генераций на сегодня"
        
        limits_data = {
            'is_premium': user.is_premium,
            'daily_limit': daily_limit,
            'used_today': used_today,
            'remaining_today': remaining_today,
            'next_reset': next_reset,
            'can_generate': can_generate,
            'limit_message': limit_message
        }
        
        serializer = AILimitsSerializer(limits_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in ai_generation_limits: {str(e)}")
        return Response({
            'error': 'Ошибка получения лимитов'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_generation_history(request):
    """История AI генераций пользователя"""
    try:
        user = request.user
        
        # Получаем историю запросов
        requests = AIGenerationRequest.objects.filter(user=user).order_by('-created_at')
        
        # Пагинация
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        offset = (page - 1) * page_size
        
        total_count = requests.count()
        requests_page = requests[offset:offset + page_size]
        
        serializer = AIGenerationRequestListSerializer(requests_page, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"Error in ai_generation_history: {str(e)}")
        return Response({
            'error': 'Ошибка получения истории'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_user_stats(request):
    """Статистика AI генераций пользователя"""
    try:
        user = request.user
        
        # Общая статистика
        total_requests = AIGenerationRequest.objects.filter(user=user).count()
        total_successful = AIGenerationRequest.objects.filter(user=user, status='success').count()
        total_failed = total_requests - total_successful
        
        # Процент успеха
        success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        # Среднее время ответа
        avg_response_time = AIGenerationRequest.objects.filter(
            user=user, 
            status='success', 
            response_time__isnull=False
        ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0
        
        # Количество созданных портфолио
        total_portfolios_created = AIGenerationRequest.objects.filter(
            user=user, 
            portfolio_created__isnull=False
        ).count()
        
        # Любимый стиль
        favorite_style_data = AIGenerationRequest.objects.filter(user=user).values('style').annotate(
            count=Count('style')
        ).order_by('-count').first()
        favorite_style = favorite_style_data['style'] if favorite_style_data else 'modern'
        
        # Статистика за сегодня
        today = timezone.now().date()
        today_stats = AIGenerationStats.objects.filter(user=user, date=today).first()
        today_requests = today_stats.requests_count if today_stats else 0
        remaining_today = max(0, 5 - today_requests) if user.is_premium else 0
        
        # Наиболее используемые промпты (последние 10)
        recent_prompts = AIGenerationRequest.objects.filter(
            user=user,
            status='success'
        ).order_by('-created_at')[:10].values_list('prompt', flat=True)
        
        stats_data = {
            'total_requests': total_requests,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'success_rate': round(success_rate, 1),
            'average_response_time': round(avg_response_time, 2),
            'total_portfolios_created': total_portfolios_created,
            'favorite_style': favorite_style,
            'today_requests': today_requests,
            'remaining_today': remaining_today,
            'most_used_prompts': list(recent_prompts)
        }
        
        serializer = AIUserStatsSerializer(stats_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in ai_user_stats: {str(e)}")
        return Response({
            'error': 'Ошибка получения статистики'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_daily_stats(request):
    """Дневная статистика AI генераций пользователя"""
    try:
        user = request.user
        
        # Получаем статистику за последние 30 дней
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        daily_stats = AIGenerationStats.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
        
        serializer = AIGenerationStatsSerializer(daily_stats, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in ai_daily_stats: {str(e)}")
        return Response({
            'error': 'Ошибка получения дневной статистики'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_style_stats(request):
    """Статистика по стилям для пользователя"""
    try:
        user = request.user
        
        # Статистика по стилям
        style_stats = AIGenerationRequest.objects.filter(user=user).values('style').annotate(
            count=Count('id'),
            successful=Count('id', filter=Q(status='success')),
            avg_response_time=Avg('response_time', filter=Q(status='success'))
        ).order_by('-count')
        
        results = []
        for stat in style_stats:
            success_rate = (stat['successful'] / stat['count'] * 100) if stat['count'] > 0 else 0
            results.append({
                'style': stat['style'],
                'count': stat['count'],
                'success_rate': round(success_rate, 1),
                'average_response_time': round(stat['avg_response_time'] or 0, 2)
            })
        
        serializer = AIStyleStatsSerializer(results, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in ai_style_stats: {str(e)}")
        return Response({
            'error': 'Ошибка получения статистики по стилям'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_prompt_templates(request):
    """Получение шаблонов промптов"""
    try:
        user = request.user
        
        # Получаем публичные шаблоны и шаблоны пользователя
        templates = AIPromptTemplate.objects.filter(
            Q(is_public=True) | Q(user=user)
        ).order_by('-is_featured', '-usage_count', '-created_at')
        
        # Фильтрация по категории
        category = request.GET.get('category')
        if category:
            templates = templates.filter(category=category)
        
        # Фильтрация по стилю
        style = request.GET.get('style')
        if style:
            templates = templates.filter(style=style)
        
        serializer = AIPromptTemplateSerializer(templates, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in ai_prompt_templates: {str(e)}")
        return Response({
            'error': 'Ошибка получения шаблонов'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_save_prompt_template(request):
    """Сохранение промпта как шаблона"""
    try:
        user = request.user
        
        # Проверяем лимит шаблонов (максимум 20 на пользователя)
        user_templates_count = AIPromptTemplate.objects.filter(user=user).count()
        if user_templates_count >= 20:
            return Response({
                'error': 'Превышен лимит шаблонов (максимум 20)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AIPromptTemplateSerializer(data=request.data)
        if serializer.is_valid():
            template = serializer.save(user=user)
            
            return Response({
                'message': 'Шаблон сохранен',
                'template': AIPromptTemplateSerializer(template).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in ai_save_prompt_template: {str(e)}")
        return Response({
            'error': 'Ошибка сохранения шаблона'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def ai_delete_prompt_template(request, template_id):
    """Удаление шаблона промпта"""
    try:
        user = request.user
        
        template = AIPromptTemplate.objects.filter(
            id=template_id,
            user=user
        ).first()
        
        if not template:
            return Response({
                'error': 'Шаблон не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        template.delete()
        
        return Response({
            'message': 'Шаблон удален'
        })
        
    except Exception as e:
        logger.error(f"Error in ai_delete_prompt_template: {str(e)}")
        return Response({
            'error': 'Ошибка удаления шаблона'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def ai_global_stats(request):
    """Глобальная статистика AI (только для админов)"""
    try:
        # Получаем статистику за последние 30 дней
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        global_stats = GlobalAIStats.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
        
        # Агрегированная статистика
        total_requests = sum(stat.total_requests for stat in global_stats)
        total_successful = sum(stat.total_successful for stat in global_stats)
        total_failed = sum(stat.total_failed for stat in global_stats)
        
        success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        return Response({
            'daily_stats': [
                {
                    'date': stat.date,
                    'total_requests': stat.total_requests,
                    'total_successful': stat.total_successful,
                    'total_failed': stat.total_failed,
                    'active_users': stat.active_users,
                    'average_response_time': stat.average_response_time,
                    'popular_styles': stat.popular_styles
                }
                for stat in global_stats
            ],
            'aggregated': {
                'total_requests': total_requests,
                'total_successful': total_successful,
                'total_failed': total_failed,
                'success_rate': round(success_rate, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in ai_global_stats: {str(e)}")
        return Response({
            'error': 'Ошибка получения глобальной статистики'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 