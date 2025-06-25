from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Portfolio
import re


class PortfolioSubdomainMiddleware(MiddlewareMixin):
    """
    Middleware для обработки субдоменов портфолио
    Поддерживает форматы:
    - portfolioname.localhost:8000 (разработка)
    - portfolioname.devcommerce.org (продакшен)
    """
    
    def process_request(self, request):
        host = request.get_host()
        
        # Проверяем, является ли это субдоменом портфолио
        if not self.is_portfolio_subdomain(host):
            return None
        
        # Извлекаем имя субдомена
        subdomain = self.extract_subdomain(host)
        
        if not subdomain:
            return None
            
        try:
            # Ищем портфолио по slug
            portfolio = get_object_or_404(
                Portfolio.objects.select_related('author'),
                slug=subdomain,
                is_public=True
            )
            
            # Увеличиваем счетчик просмотров
            portfolio.views += 1
            portfolio.save(update_fields=['views'])
            
            # Генерируем HTML страницу портфолио
            html_content = self.generate_portfolio_html(portfolio, subdomain)
            
            return HttpResponse(
                html_content,
                content_type='text/html; charset=utf-8'
            )
            
        except Http404:
            # Портфолио не найдено
            return HttpResponse(
                self.get_not_found_html(subdomain),
                status=404,
                content_type='text/html; charset=utf-8'
            )
        except Exception as e:
            # Ошибка сервера
            return HttpResponse(
                self.get_error_html(subdomain, str(e)),
                status=500,
                content_type='text/html; charset=utf-8'
            )
    
    def is_portfolio_subdomain(self, host):
        """Проверяет, является ли хост субдоменом портфолио"""
        if not host:
            return False
            
        # Паттерны для разных окружений
        patterns = [
            r'^[\w-]+\.localhost:8000$',        # Разработка
            r'^[\w-]+\.devcommerce\.org$',      # Продакшен
            r'^[\w-]+\.127\.0\.0\.1:8000$',     # Альтернативная разработка
        ]
        
        # Исключенные субдомены
        excluded_subdomains = ['www', 'api', 'admin', 'app', 'mail', 'blog', 'cdn']
        subdomain = self.extract_subdomain(host)
        
        if subdomain in excluded_subdomains:
            return False
        
        return any(re.match(pattern, host) for pattern in patterns)
    
    def extract_subdomain(self, host):
        """Извлекает имя субдомена из хоста"""
        if not host:
            return None
            
        # Убираем порт, если есть
        host_without_port = host.split(':')[0]
        parts = host_without_port.split('.')
        
        # Возвращаем первую часть как субдомен
        return parts[0] if len(parts) > 1 else None
    
    def generate_portfolio_html(self, portfolio, subdomain):
        """Генерирует HTML страницу портфолио"""
        
        # Базовый URL для ссылок
        base_url = f"https://{subdomain}.devcommerce.org" if 'devcommerce.org' in subdomain else f"http://{subdomain}.localhost:8000"
        
        html_template = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ portfolio.title }} - {{ portfolio.author.username }}</title>
    <meta name="description" content="{{ portfolio.description }}">
    <meta name="author" content="{{ portfolio.author.username }}">
    <meta name="keywords" content="{{ tags }}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{{ portfolio.title }}">
    <meta property="og:description" content="{{ portfolio.description }}">
    <meta property="og:url" content="{{ base_url }}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{{ portfolio.title }}">
    <meta name="twitter:description" content="{{ portfolio.description }}">
    
    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎨</text></svg>">
    
    <style>
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* DevCommerce Branding */
        .devcommerce-badge {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 9999;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .devcommerce-badge:hover {
            background: rgba(0, 0, 0, 0.9);
            transform: translateY(-2px);
        }
        
        /* User styles */
        {{ portfolio.css_content|safe }}
    </style>
</head>
<body>
    <!-- Portfolio content -->
    {{ portfolio.html_content|safe }}
    
    <!-- DevCommerce Badge -->
    <a href="https://devcommerce.org" class="devcommerce-badge" target="_blank">
        Powered by DevCommerce
    </a>
    
    <!-- Portfolio metadata (hidden) -->
    <div id="portfolio-info" style="display: none;">
        <div class="portfolio-meta">
            <h1>{{ portfolio.title }}</h1>
            <p>{{ portfolio.description }}</p>
            <p>Автор: {{ portfolio.author.username }}</p>
            <p>Теги: {{ tags }}</p>
        </div>
    </div>
    
    <script>
        // User JavaScript
        {{ portfolio.js_content|safe }}
        
        // Portfolio metadata
        window.portfolioMeta = {
            id: "{{ portfolio.id }}",
            title: "{{ portfolio.title }}",
            description: "{{ portfolio.description }}",
            author: "{{ portfolio.author.username }}",
            tags: {{ tags_json|safe }},
            views: {{ portfolio.views }},
            likes: {{ portfolio.likes }},
            subdomain: "{{ subdomain }}"
        };
        
        console.log('📊 Portfolio loaded:', window.portfolioMeta);
    </script>
</body>
</html>"""
        
        template = Template(html_template)
        context = Context({
            'portfolio': portfolio,
            'subdomain': subdomain,
            'base_url': base_url,
            'tags': ', '.join(portfolio.tags) if portfolio.tags else '',
            'tags_json': portfolio.tags if portfolio.tags else []
        })
        
        return template.render(context)
    
    def get_not_found_html(self, subdomain):
        """HTML для страницы 404"""
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Портфолио не найдено - DevCommerce</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .error-container {{
            text-align: center;
            max-width: 500px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .error-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
        h1 {{ font-size: 2rem; margin-bottom: 1rem; font-weight: 600; }}
        p {{ font-size: 1.1rem; margin-bottom: 1.5rem; opacity: 0.9; }}
        .subdomain {{
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 10px;
            border-radius: 10px;
            font-family: monospace;
            font-weight: bold;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            margin: 10px;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .btn-primary {{
            background: white;
            color: #667eea;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">🔍</div>
        <h1>Портфолио не найдено</h1>
        <p>Портфолио <span class="subdomain">{subdomain}</span> не существует или не является публичным</p>
        <a href="http://localhost:3005" class="btn btn-primary">🏠 На главную</a>
        <a href="http://localhost:3005/auth" class="btn btn-primary">🚀 Создать портфолио</a>
    </div>
</body>
</html>"""
    
    def get_error_html(self, subdomain, error_message):
        """HTML для страницы ошибки сервера"""
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ошибка сервера - DevCommerce</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .error-container {{
            text-align: center;
            max-width: 500px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .error-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
        h1 {{ font-size: 2rem; margin-bottom: 1rem; font-weight: 600; }}
        p {{ font-size: 1.1rem; margin-bottom: 1.5rem; opacity: 0.9; }}
        .subdomain {{
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 10px;
            border-radius: 10px;
            font-family: monospace;
            font-weight: bold;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            margin: 10px;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .btn-primary {{
            background: white;
            color: #ee5a24;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">💥</div>
        <h1>500 - Ошибка сервера</h1>
        <p>Произошла ошибка при загрузке портфолио <span class="subdomain">{subdomain}</span></p>
        <p style="font-size: 0.9rem; opacity: 0.7;">Техническая информация: {error_message}</p>
        <a href="http://localhost:3005" class="btn btn-primary">🏠 На главную</a>
    </div>
</body>
</html>""" 