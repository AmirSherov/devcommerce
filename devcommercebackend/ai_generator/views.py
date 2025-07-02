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
    AIGenerationRequestListSerializer, AIGenerationStatsSerializer,
    AIPromptTemplateSerializer, AIUserStatsSerializer,
    AILimitsSerializer, AIStyleStatsSerializer,
    AIGenerationRequestSerializer
)
from .smart_generator import SmartAIGenerator
from .image_service import upload_user_profile_photo, upload_user_diploma_image

logger = logging.getLogger(__name__)
User = get_user_model()


# Старый генератор удален - используйте smart-generate


class SmartAIGenerationView(APIView):
    """
    🚀 РЕВОЛЮЦИОННЫЙ AI ГЕНЕРАТОР ПОРТФОЛИО МИРОВОГО УРОВНЯ!
    
    Теперь с 7-шаговым процессом премиум генерации, загрузкой изображений и S3 интеграцией!
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Генерация персонального портфолио через ПРЕМИУМ AI процесс"""
        
        try:
            # 🔧 ИСПРАВЛЯЕМ ОБРАБОТКУ FORMDATA С ФАЙЛАМИ
            
            # Если данные приходят как FormData (с файлами), парсим JSON строки
            if request.content_type and 'multipart/form-data' in request.content_type:
                logger.info("📦 Обрабатываем FormData с файлами")
                
                # Парсим JSON данные из FormData
                try:
                    import json
                    
                    # Логируем что приходит в FormData
                    logger.info(f"📋 FormData ключи: {list(request.data.keys())}")
                    logger.info(f"📁 FILES ключи: {list(request.FILES.keys())}")
                    
                    personal_info = json.loads(request.data.get('personal_info', '{}'))
                    education_data = json.loads(request.data.get('education', '{}'))
                    experience = json.loads(request.data.get('experience', '[]'))
                    skills = json.loads(request.data.get('skills', '{}'))
                    projects = json.loads(request.data.get('projects', '[]'))
                    contacts = json.loads(request.data.get('contacts', '{}'))
                    design_preferences = json.loads(request.data.get('design_preferences', '{}'))
                    
                    profile_photo = request.FILES.get('profile_photo')
                    diploma_image = request.FILES.get('diplomaImage')
                    
                    logger.info(f"📸 profile_photo: {profile_photo.name if profile_photo else 'None'}")
                    logger.info(f"🎓 diploma_image: {diploma_image.name if diploma_image else 'None'}")
                    
                    # Добавляем файл диплома к education
                    education = education_data.copy()
                    if diploma_image:
                        education['diplomaImage'] = diploma_image
                    
                    logger.info(f"✅ Данные распарсены: personal_info={bool(personal_info)}, education={bool(education)}")
                    
                    # 🔍 Базовая валидация данных из FormData. Упрощена.
                    validation_errors = {}
                    
                    # Проверяем обязательные поля personal_info
                    if not personal_info.get('firstName') or not personal_info.get('lastName') or not personal_info.get('profession'):
                        validation_errors.setdefault('personal_info', []).append('Имя, фамилия и профессия обязательны')
                    
                    # Проверяем skills
                    if not skills.get('technical'):
                        validation_errors.setdefault('skills', []).append('Добавьте хотя бы один технический навык')
                    
                    # Проверяем contacts
                    if not contacts.get('email'):
                        validation_errors.setdefault('contacts', []).append('Email обязателен')
                    
                    if validation_errors:
                        logger.error(f"❌ Ошибки валидации FormData: {validation_errors}")
                        return Response({
                            'success': False,
                            'error': 'Данные не прошли валидацию',
                            'details': validation_errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    logger.info("✅ Валидация FormData прошла успешно")
                    
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"❌ Ошибка парсинга FormData: {str(e)}")
                    return Response({
                        'success': False,
                        'error': 'Ошибка обработки данных с файлами',
                        'details': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                # Обычная JSON обработка
                logger.info("📝 Обрабатываем обычный JSON")
                serializer = AIGenerationRequestSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response({
                        'success': False,
                        'error': 'Некорректные данные',
                        'details': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Извлекаем данные из сериализатора
                personal_info = serializer.validated_data['personal_info']
                # Поля education, experience, projects больше не обязательны
                education = serializer.validated_data.get('education', {})
                experience = serializer.validated_data.get('experience', [])
                skills = serializer.validated_data['skills']
                projects = serializer.validated_data.get('projects', [])
                contacts = serializer.validated_data['contacts']
                design_preferences = serializer.validated_data['design_preferences']
                profile_photo = serializer.validated_data.get('profile_photo')
            
            # 🖼️ ОБРАБОТКА ИЗОБРАЖЕНИЙ
            profile_photo_data = None
            diploma_image_url = None
            
            # Загружаем фото профиля если есть
            if profile_photo:
                logger.info(f"📸 Загружаем фото профиля для {request.user.username}")
                photo_result = upload_user_profile_photo(request.user, profile_photo)
                if photo_result:
                    profile_photo_url, ai_analysis = photo_result
                    profile_photo_data = {
                        'url': profile_photo_url,
                        'ai_analysis': ai_analysis
                    }
                    logger.info(f"✅ Фото профиля загружено: {profile_photo_url}")
                else:
                    logger.warning("⚠️ Не удалось загрузить фото профиля")
            
            # Загружаем диплом если есть
            diploma_image = education.get('diplomaImage') if isinstance(education, dict) else getattr(education, 'diplomaImage', None)
            if diploma_image:
                logger.info(f"🎓 Загружаем диплом для {request.user.username}")
                diploma_image_url = upload_user_diploma_image(request.user, diploma_image)
                if diploma_image_url:
                    logger.info(f"✅ Диплом загружен: {diploma_image_url}")
                else:
                    logger.warning("⚠️ Не удалось загрузить диплом")
            
            # Формируем название портфолио
            full_name = f"{personal_info['firstName']} {personal_info['lastName']}"
            portfolio_title = f"Портфолио {full_name} - {personal_info['profession']}"
            
            # Подготавливаем данные для AI генерации
            request_data = {
                'user': request.user,
                'title': portfolio_title,
                'personal_info': personal_info,
                'education': education,
                'experience': experience,
                'skills': skills,
                'projects': projects,
                'contacts': contacts,
                'design_preferences': design_preferences,
                'profile_photo_data': profile_photo_data,  # Включаем данные фото
                'diploma_image_url': diploma_image_url,    # Включаем URL диплома
                'portfolio_type': 'personal'
            }
            
            logger.info(f"🚀 [PREMIUM AI] Запрос СУПЕР генерации от {request.user.username}")
            if profile_photo_data:
                logger.info("🎨 + Персональное фото для уникального дизайна")
            if diploma_image_url:
                logger.info("🎓 + Диплом для подтверждения образования")
            
            # Создаем AI генератор с одним оптимизированным запросом
            generator = SmartAIGenerator()
            result = generator.generate_portfolio_optimized(request_data)
            
            if result['success']:
                logger.info(f"🎉 [PREMIUM AI] ✅ ШЕДЕВР с изображениями создан для {request.user.username}!")
                
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
                        'process_type': 'premium_7_step_with_images'
                    },
                    'premium_features': {
                        'personal_analysis': True,
                        'career_optimization': True,
                        'skills_highlighting': True,
                        'projects_showcase': True,
                        'unique_design': True,
                        'professional_styling': True,
                        'responsive_layout': True,
                        'profile_photo_integration': profile_photo_data is not None,
                        'diploma_verification': diploma_image_url is not None,
                        'ai_photo_analysis': profile_photo_data is not None
                    },
                    'images_data': {
                        'profile_photo': profile_photo_data,
                        'diploma_image': diploma_image_url,
                        'ai_recommendations': profile_photo_data.get('ai_analysis', {}).get('ai_recommendations', []) if profile_photo_data else []
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


# Премиум генератор с прогрессом удален - используйте smart-generate


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