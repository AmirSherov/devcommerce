from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import Portfolio, PortfolioLike, PortfolioView
from .serializers import (
    PortfolioListSerializer, PortfolioDetailSerializer,
    PortfolioCreateSerializer, PortfolioUpdateSerializer,
    PortfolioCodeUpdateSerializer, PortfolioStatsSerializer,
    UserPortfolioStatsSerializer
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class PortfolioPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50
def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def portfolio_list(request):
    """Get list of public portfolios"""
    try:
        portfolios = Portfolio.objects.filter(is_public=True).select_related('author')
        search = request.GET.get('search', '')
        if search:
            portfolios = portfolios.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(author__username__icontains=search) |
                Q(tags__icontains=search)
            )
        tags = request.GET.get('tags', '')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                portfolios = portfolios.filter(tags__icontains=tag)
        order_by = request.GET.get('order_by', '-updated_at')
        if order_by in ['-updated_at', '-created_at', '-views', '-likes', 'title']:
            portfolios = portfolios.order_by(order_by)
        paginator = PortfolioPagination()
        page = paginator.paginate_queryset(portfolios, request)
        serializer = PortfolioListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in portfolio_list: {e}")
        return Response({
            'error': 'Failed to fetch portfolios'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_portfolios(request):
    """Get current user's portfolios"""
    try:
        portfolios = Portfolio.objects.filter(author=request.user).order_by('-updated_at')
        serializer = PortfolioDetailSerializer(portfolios, many=True)
        
        return Response({
            'portfolios': serializer.data,
            'count': portfolios.count(),
            'remaining_slots': max(0, 5 - portfolios.count())
        })
        
    except Exception as e:
        logger.error(f"Error in my_portfolios: {e}")
        return Response({
            'error': 'Failed to fetch your portfolios'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_portfolio(request):
    """Create new portfolio"""
    try:
        serializer = PortfolioCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            with transaction.atomic():
                portfolio = serializer.save()
                
                return Response({
                    'message': 'Portfolio created successfully',
                    'portfolio': PortfolioDetailSerializer(portfolio).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in create_portfolio: {e}")
        return Response({
            'error': 'Failed to create portfolio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def portfolio_detail(request, portfolio_id):
    """Get portfolio details"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        if not portfolio.is_public and portfolio.author != request.user:
            return Response({
                'error': 'Portfolio not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            ip_address = get_client_ip(request)
            view, created = PortfolioView.objects.get_or_create(
                portfolio=portfolio,
                ip_address=ip_address,
                defaults={'user': request.user}
            )
            if created:
                portfolio.views += 1
                portfolio.save(update_fields=['views'])
        
        serializer = PortfolioDetailSerializer(portfolio)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in portfolio_detail: {e}")
        return Response({
            'error': 'Failed to fetch portfolio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_portfolio(request, portfolio_id):
    """Update portfolio"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, author=request.user)
        
        serializer = PortfolioUpdateSerializer(portfolio, data=request.data, partial=True)
        
        if serializer.is_valid():
            with transaction.atomic():
                portfolio = serializer.save()
                
                return Response({
                    'message': 'Portfolio updated successfully',
                    'portfolio': PortfolioDetailSerializer(portfolio).data
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in update_portfolio: {e}")
        return Response({
            'error': 'Failed to update portfolio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def autosave_portfolio(request, portfolio_id):
    """Autosave portfolio code (for live editing)"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, author=request.user)
        
        serializer = PortfolioCodeUpdateSerializer(portfolio, data=request.data, partial=True)
        
        if serializer.is_valid():
            portfolio = serializer.save()
            
            return Response({
                'message': 'Portfolio autosaved successfully',
                'updated_at': portfolio.updated_at
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in autosave_portfolio: {e}")
        return Response({
            'error': 'Failed to autosave portfolio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_portfolio(request, portfolio_id):
    """Delete portfolio"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, author=request.user)
        
        with transaction.atomic():
            portfolio.delete()
            
            return Response({
                'message': 'Portfolio deleted successfully'
            })
        
    except Exception as e:
        logger.error(f"Error in delete_portfolio: {e}")
        return Response({
            'error': 'Failed to delete portfolio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_portfolio_like(request, portfolio_id):
    """Toggle like on portfolio"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, is_public=True)
        
        like, created = PortfolioLike.objects.get_or_create(
            portfolio=portfolio,
            user=request.user
        )
        
        if created:
            portfolio.likes += 1
            portfolio.save(update_fields=['likes'])
            message = 'Portfolio liked'
            liked = True
        else:
            like.delete()
            portfolio.likes = max(0, portfolio.likes - 1)
            portfolio.save(update_fields=['likes'])
            message = 'Portfolio unliked'
            liked = False
        
        return Response({
            'message': message,
            'liked': liked,
            'likes_count': portfolio.likes
        })
        
    except Exception as e:
        logger.error(f"Error in toggle_portfolio_like: {e}")
        return Response({
            'error': 'Failed to toggle like'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_portfolios(request, username):
    """Get public portfolios of a specific user"""
    try:
        user = get_object_or_404(User, username=username)
        portfolios = Portfolio.objects.filter(author=user, is_public=True).order_by('-updated_at')
        
        # Pagination
        paginator = PortfolioPagination()
        page = paginator.paginate_queryset(portfolios, request)
        serializer = PortfolioListSerializer(page, many=True)
        
        return paginator.get_paginated_response({
            'user': {
                'username': user.username,
                'full_name': user.full_name,
            },
            'portfolios': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error in user_portfolios: {e}")
        return Response({
            'error': 'Failed to fetch user portfolios'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_portfolio_stats(request):
    """Get current user's portfolio statistics"""
    try:
        portfolios = Portfolio.objects.filter(author=request.user)
        
        stats = {
            'portfolios_count': portfolios.count(),
            'remaining_slots': max(0, 5 - portfolios.count()),
            'total_views': portfolios.aggregate(Sum('views'))['views__sum'] or 0,
            'total_likes': portfolios.aggregate(Sum('likes'))['likes__sum'] or 0,
            'most_viewed_portfolio': None,
            'most_liked_portfolio': None,
        }
        
        # Most viewed portfolio
        most_viewed = portfolios.order_by('-views').first()
        if most_viewed:
            stats['most_viewed_portfolio'] = PortfolioListSerializer(most_viewed).data
        
        # Most liked portfolio
        most_liked = portfolios.order_by('-likes').first()
        if most_liked:
            stats['most_liked_portfolio'] = PortfolioListSerializer(most_liked).data
        
        serializer = UserPortfolioStatsSerializer(stats)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in my_portfolio_stats: {e}")
        return Response({
            'error': 'Failed to fetch portfolio statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def portfolio_stats(request):
    """Get global portfolio statistics"""
    try:
        total_portfolios = Portfolio.objects.count()
        public_portfolios = Portfolio.objects.filter(is_public=True).count()
        
        stats = {
            'total_portfolios': total_portfolios,
            'total_views': Portfolio.objects.aggregate(Sum('views'))['views__sum'] or 0,
            'total_likes': Portfolio.objects.aggregate(Sum('likes'))['likes__sum'] or 0,
            'public_portfolios': public_portfolios,
            'private_portfolios': total_portfolios - public_portfolios,
        }
        
        serializer = PortfolioStatsSerializer(stats)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in portfolio_stats: {e}")
        return Response({
            'error': 'Failed to fetch portfolio statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_portfolio_site(request, portfolio_id):
    """Render public portfolio site by ID"""
    try:
        # Get portfolio - only if it's public
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, is_public=True)
        
        # Record view (anonymous or authenticated)
        try:
            user = request.user if request.user.is_authenticated else None
            PortfolioView.objects.get_or_create(
                portfolio=portfolio,
                user=user,
                defaults={'ip_address': request.META.get('REMOTE_ADDR', '')}
            )
        except Exception as e:
            logger.warning(f"Failed to record view for portfolio {portfolio_id}: {e}")
        
        # Create full HTML page
        full_html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{portfolio.title} - {portfolio.author.username}</title>
    <meta name="description" content="{portfolio.description}">
    <meta name="author" content="{portfolio.author.username}">
    <meta name="keywords" content="{', '.join(portfolio.tags)}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{request.build_absolute_uri()}">
    <meta property="og:title" content="{portfolio.title}">
    <meta property="og:description" content="{portfolio.description}">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary">
    <meta property="twitter:url" content="{request.build_absolute_uri()}">
    <meta property="twitter:title" content="{portfolio.title}">
    <meta property="twitter:description" content="{portfolio.description}">
    
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        /* User styles */
        {portfolio.css_content}
    </style>
</head>
<body>
    <!-- Portfolio content -->
    {portfolio.html_content}
    
    <!-- Portfolio info (hidden by default, can be styled by user) -->
    <div id="portfolio-info" style="display: none;">
        <div class="portfolio-meta">
            <h1>{portfolio.title}</h1>
            <p>{portfolio.description}</p>
            <p>Автор: {portfolio.author.username}</p>
            <p>Теги: {', '.join(portfolio.tags)}</p>
        </div>
    </div>
    
    <script>
        // User JavaScript
        {portfolio.js_content}
        
        // Portfolio metadata (available globally)
        window.portfolioMeta = {{
            id: "{portfolio.id}",
            title: "{portfolio.title}",
            description: "{portfolio.description}",
            author: "{portfolio.author.username}",
            tags: {portfolio.tags},
            views: {portfolio.views},
            likes: {portfolio.likes}
        }};
    </script>
</body>
</html>'''
        
        return HttpResponse(full_html, content_type='text/html; charset=utf-8')
        
    except Portfolio.DoesNotExist:
        # Return 404 page
        return HttpResponse(
            '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Портфолио не найдено</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .error { color: #e74c3c; }
        .message { margin: 20px 0; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="error">
        <h1>404 - Портфолио не найдено</h1>
        <div class="message">
            <p>Портфолио не существует или не является публичным</p>
            <p><a href="/">← Вернуться на главную</a></p>
        </div>
    </div>
</body>
</html>''',
            content_type='text/html; charset=utf-8',
            status=404
        )
        
    except Exception as e:
        logger.error(f"Error serving portfolio {portfolio_id}: {e}")
        return HttpResponse(
            '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ошибка сервера</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .error { color: #e74c3c; }
        .message { margin: 20px 0; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="error">
        <h1>500 - Ошибка сервера</h1>
        <div class="message">
            <p>Произошла ошибка при загрузке портфолио</p>
            <p><a href="/">← Вернуться на главную</a></p>
        </div>
    </div>
</body>
</html>''',
            content_type='text/html; charset=utf-8',
            status=500
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_portfolio_by_slug(request, slug):
    """Get portfolio by slug for subdomain rendering"""
    try:
        # Get portfolio by slug - only if it's public
        portfolio = get_object_or_404(Portfolio, slug=slug, is_public=True)
        
        # Serialize portfolio data
        serializer = PortfolioDetailSerializer(portfolio)
        
        return Response(serializer.data)
        
    except Portfolio.DoesNotExist:
        return Response({
            'error': 'Portfolio not found or not public'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error in get_portfolio_by_slug: {e}")
        return Response({
            'error': 'Failed to fetch portfolio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def record_portfolio_view_api(request, portfolio_id):
    """Record portfolio view (for subdomain access)"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, is_public=True)
        
        # Record view (anonymous or authenticated)
        user = request.user if request.user.is_authenticated else None
        ip_address = get_client_ip(request)
        
        PortfolioView.objects.get_or_create(
            portfolio=portfolio,
            user=user,
            defaults={'ip_address': ip_address}
        )
        
        return Response({'message': 'View recorded successfully'})
        
    except Portfolio.DoesNotExist:
        return Response({
            'error': 'Portfolio not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error in record_portfolio_view_api: {e}")
        return Response({
            'error': 'Failed to record view'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
