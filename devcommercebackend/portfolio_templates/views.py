from django.shortcuts import render
import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.http import HttpResponse
from django.template import Template, Context
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from portfolio.models import Portfolio

from .models import PortfolioTemplate, TemplateUsage, TemplateLike
from .serializers import (
    PortfolioTemplateListSerializer,
    PortfolioTemplateDetailSerializer,
    PortfolioTemplateCreateSerializer,
    TemplateUsageSerializer,
    TemplateLikeSerializer,
    TemplateStatsSerializer,
    UseTemplateSerializer
)

logger = logging.getLogger(__name__)


class TemplatePagination(PageNumberPagination):
    """Пагинация для шаблонов"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


class PortfolioTemplateListView(APIView):
    """
    📋 API ДЛЯ ПОЛУЧЕНИЯ СПИСКА ШАБЛОНОВ
    
    GET /api/templates/ - список всех активных шаблонов
    """
    
    permission_classes = [permissions.AllowAny]
    pagination_class = TemplatePagination
    
    def get(self, request):
        """Получение списка шаблонов с фильтрацией и поиском"""
        
        try:
            # Базовый queryset - только активные шаблоны
            queryset = PortfolioTemplate.objects.filter(is_active=True)
            
            # Фильтрация по категории
            category = request.GET.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Фильтрация по сложности
            difficulty = request.GET.get('difficulty')
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)
            
            # Фильтрация по премиум статусу
            is_premium = request.GET.get('is_premium')
            if is_premium is not None:
                queryset = queryset.filter(is_premium=is_premium.lower() == 'true')
            
            # Фильтрация только рекомендуемых
            featured_only = request.GET.get('featured')
            if featured_only and featured_only.lower() == 'true':
                queryset = queryset.filter(is_featured=True)
            
            # Поиск по названию, описанию и тегам
            search = request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(tags__icontains=search)
                )
            
            # Сортировка
            sort_by = request.GET.get('sort', 'featured')  # По умолчанию - рекомендуемые
            
            if sort_by == 'popular':
                queryset = queryset.order_by('-likes', '-views')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'most_used':
                queryset = queryset.order_by('-uses')
            elif sort_by == 'alphabetical':
                queryset = queryset.order_by('title')
            else:  # featured (по умолчанию)
                queryset = queryset.order_by('-is_featured', '-likes', '-created_at')
            
            # Пагинация
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = PortfolioTemplateListSerializer(
                    page, 
                    many=True, 
                    context={'request': request}
                )
                return paginator.get_paginated_response(serializer.data)
            
            # Fallback без пагинации
            serializer = PortfolioTemplateListSerializer(
                queryset, 
                many=True, 
                context={'request': request}
            )
            
            return Response({
                'success': True,
                'data': serializer.data,
                'count': queryset.count()
            })
            
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка получения списка шаблонов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения списка шаблонов'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PortfolioTemplateDetailView(APIView):
    """
    📄 API ДЛЯ ПОЛУЧЕНИЯ ДЕТАЛЬНОЙ ИНФОРМАЦИИ О ШАБЛОНЕ
    
    GET /api/templates/{id}/ - детальная информация о шаблоне
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, template_id):
        """Получение детальной информации о шаблоне"""
        
        try:
            template = get_object_or_404(
                PortfolioTemplate, 
                id=template_id, 
                is_active=True
            )
            
            # Увеличиваем счетчик просмотров
            template.increment_views()
            
            serializer = PortfolioTemplateDetailSerializer(
                template, 
                context={'request': request}
            )
            
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except PortfolioTemplate.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Шаблон не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка получения шаблона {template_id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения шаблона'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PortfolioTemplatePreviewView(APIView):
    """
    👁️ API ДЛЯ ПРЕВЬЮ ШАБЛОНА
    
    GET /api/templates/{id}/preview/ - HTML превью шаблона
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, template_id):
        """Получение HTML превью шаблона"""
        
        try:
            template = get_object_or_404(
                PortfolioTemplate, 
                id=template_id, 
                is_active=True
            )
            
            # Увеличиваем счетчик просмотров
            template.increment_views()
            
            # Проверяем наличие контента
            if not template.html_code.strip() or not template.css_code.strip():
                # Показываем заглушку, если нет контента
                full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template.title} - Превью</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .preview-placeholder {{
            background: white;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 500px;
        }}
        .preview-placeholder h1 {{
            color: #333;
            margin-bottom: 16px;
            font-size: 24px;
        }}
        .preview-placeholder p {{
            color: #666;
            line-height: 1.6;
            margin: 0;
        }}
        .template-info {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}
        .badge {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 4px;
        }}
    </style>
</head>
<body>
    <div class="preview-placeholder">
        <h1>🎨 {template.title}</h1>
        <p>{template.description}</p>
        <div class="template-info">
            <div class="badge">{template.get_category_display()}</div>
            <div class="badge">{template.get_difficulty_display()}</div>
            <p style="margin-top: 15px; font-size: 14px; color: #888;">
                Превью будет доступно после добавления HTML/CSS кода в админке
            </p>
        </div>
    </div>
</body>
</html>"""
            else:
                # Формируем полный HTML для превью
                full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template.title} - Превью</title>
    <style>
        {template.css_code}
    </style>
</head>
<body>
    {template.html_code}
    <script>
        {template.js_code or ''}
    </script>
</body>
</html>"""
            
            response = HttpResponse(full_html, content_type='text/html')
            # Убираем X-Frame-Options чтобы разрешить отображение в iframe
            # Используем современный CSP подход
            response['Content-Security-Policy'] = "frame-ancestors *;"
            # Добавляем CORS заголовки для предпросмотра
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
            
        except PortfolioTemplate.DoesNotExist:
            return HttpResponse(
                '<h1>Шаблон не найден</h1>', 
                content_type='text/html',
                status=404
            )
        
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка превью шаблона {template_id}: {str(e)}")
            return HttpResponse(
                '<h1>Ошибка загрузки превью</h1>', 
                content_type='text/html',
                status=500
            )


class UseTemplateView(APIView):
    """
    🎯 API ДЛЯ ИСПОЛЬЗОВАНИЯ ШАБЛОНА
    
    POST /api/templates/use/ - использование шаблона для создания портфолио
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Использование шаблона для создания портфолио"""
        
        try:
            serializer = UseTemplateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            template_id = serializer.validated_data['template_id']
            template = get_object_or_404(
                PortfolioTemplate, 
                id=template_id, 
                is_active=True
            )
            
            # Проверяем премиум доступ
            if template.is_premium and not request.user.is_premium:
                return Response({
                    'success': False,
                    'error': 'Премиум шаблон доступен только Premium пользователям',
                    'error_code': 'PREMIUM_REQUIRED'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Создаем портфолио на основе шаблона
            portfolio_title = serializer.validated_data.get(
                'portfolio_title', 
                f"{template.title} - {request.user.username}"
            )
            
            portfolio_description = serializer.validated_data.get(
                'portfolio_description',
                f"Портфолио создано на основе шаблона '{template.title}'"
            )
            
            # Создаем портфолио
            portfolio = Portfolio.objects.create(
                author=request.user,
                title=portfolio_title,
                description=portfolio_description,
                html_content=template.html_code,
                css_content=template.css_code,
                js_content=template.js_code,
                tags=template.tags + ['template-based'],
                is_public=False  # По умолчанию приватное
            )
            
            # Записываем использование шаблона
            TemplateUsage.objects.create(
                template=template,
                user=request.user,
                portfolio_created=portfolio
            )
            
            # Увеличиваем счетчик использований
            template.increment_uses()
            
            logger.info(f"[TEMPLATES] Пользователь {request.user.username} использовал шаблон {template.title}")
            
            return Response({
                'success': True,
                'portfolio': {
                    'id': str(portfolio.id),
                    'title': portfolio.title,
                    'slug': portfolio.slug,
                    'edit_url': f'/portfolio/edit/me?project={portfolio.id}',
                    'public_url': portfolio.public_url if portfolio.is_public else None
                },
                'template': {
                    'id': template.id,
                    'title': template.title,
                    'category': template.category
                },
                'message': 'Портфолио успешно создано на основе шаблона'
            }, status=status.HTTP_201_CREATED)
            
        except PortfolioTemplate.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Шаблон не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка использования шаблона: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка создания портфолио на основе шаблона'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateLikeView(APIView):
    """
    👍 API ДЛЯ ЛАЙКОВ ШАБЛОНОВ
    
    POST /api/templates/{id}/like/ - лайкнуть шаблон
    DELETE /api/templates/{id}/like/ - убрать лайк
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, template_id):
        """Лайкнуть шаблон"""
        
        try:
            template = get_object_or_404(
                PortfolioTemplate, 
                id=template_id, 
                is_active=True
            )
            
            # Проверяем, не лайкнул ли уже пользователь
            like, created = TemplateLike.objects.get_or_create(
                template=template,
                user=request.user
            )
            
            if created:
                # Увеличиваем счетчик лайков
                template.add_like()
                
                return Response({
                    'success': True,
                    'message': 'Лайк добавлен',
                    'likes_count': template.likes
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Вы уже лайкнули этот шаблон',
                    'likes_count': template.likes
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except PortfolioTemplate.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Шаблон не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка лайка шаблона {template_id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка добавления лайка'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, template_id):
        """Убрать лайк с шаблона"""
        
        try:
            template = get_object_or_404(
                PortfolioTemplate, 
                id=template_id, 
                is_active=True
            )
            
            # Пытаемся найти и удалить лайк
            try:
                like = TemplateLike.objects.get(
                    template=template,
                    user=request.user
                )
                like.delete()
                
                # Уменьшаем счетчик лайков
                template.remove_like()
                
                return Response({
                    'success': True,
                    'message': 'Лайк убран',
                    'likes_count': template.likes
                })
                
            except TemplateLike.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Вы не лайкали этот шаблон',
                    'likes_count': template.likes
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except PortfolioTemplate.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Шаблон не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка удаления лайка шаблона {template_id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка удаления лайка'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateStatsView(APIView):
    """
    📈 API ДЛЯ СТАТИСТИКИ ШАБЛОНОВ
    
    GET /api/templates/stats/ - общая статистика
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Получение статистики шаблонов"""
        
        try:
            # Общая статистика
            total_templates = PortfolioTemplate.objects.count()
            active_templates = PortfolioTemplate.objects.filter(is_active=True).count()
            featured_templates = PortfolioTemplate.objects.filter(is_featured=True, is_active=True).count()
            premium_templates = PortfolioTemplate.objects.filter(is_premium=True, is_active=True).count()
            
            # Агрегированная статистика
            from django.db.models import Sum
            total_likes = PortfolioTemplate.objects.filter(is_active=True).aggregate(Sum('likes'))['likes__sum'] or 0
            total_views = PortfolioTemplate.objects.filter(is_active=True).aggregate(Sum('views'))['views__sum'] or 0
            total_uses = PortfolioTemplate.objects.filter(is_active=True).aggregate(Sum('uses'))['uses__sum'] or 0
            
            # Популярные категории
            popular_categories = (
                PortfolioTemplate.objects
                .filter(is_active=True)
                .values('category', 'category')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
            
            # Последние шаблоны
            recent_templates = PortfolioTemplate.objects.filter(
                is_active=True
            ).order_by('-created_at')[:5]
            
            recent_templates_data = PortfolioTemplateListSerializer(
                recent_templates, 
                many=True,
                context={'request': request}
            ).data
            
            stats_data = {
                'total_templates': total_templates,
                'active_templates': active_templates,
                'featured_templates': featured_templates,
                'premium_templates': premium_templates,
                'total_likes': total_likes,
                'total_views': total_views,
                'total_uses': total_uses,
                'popular_categories': list(popular_categories),
                'recent_templates': recent_templates_data
            }
            
            serializer = TemplateStatsSerializer(stats_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"[TEMPLATES] Ошибка получения статистики: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения статистики'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def template_categories_view(request):
    """
    🏷️ API ДЛЯ ПОЛУЧЕНИЯ СПИСКА КАТЕГОРИЙ
    
    GET /api/templates/categories/ - список всех доступных категорий
    """
    
    try:
        # Получаем категории с количеством активных шаблонов
        categories_with_counts = (
            PortfolioTemplate.objects
            .filter(is_active=True)
            .values('category')
            .annotate(count=Count('id'))
            .order_by('category')
        )
        
        # Формируем список с человекочитаемыми названиями
        categories = []
        for item in categories_with_counts:
            category_code = item['category']
            category_display = dict(PortfolioTemplate.CATEGORY_CHOICES).get(category_code, category_code)
            
            categories.append({
                'code': category_code,
                'display': category_display,
                'count': item['count']
            })
        
        return Response({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        logger.error(f"[TEMPLATES] Ошибка получения категорий: {str(e)}")
        return Response({
            'success': False,
            'error': 'Ошибка получения категорий'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
