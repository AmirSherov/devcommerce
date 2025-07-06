import time
import logging
import re
from typing import Dict, Any
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from openai import OpenAI
from portfolio.models import Portfolio
from portfolio_templates.models import PortfolioTemplate
from .models import TemplateAIGeneration, TemplateAIStats

logger = logging.getLogger(__name__)
User = get_user_model()


class TemplateAIService:
    """
    🤖 СЕРВИС ДЛЯ AI ЗАПОЛНЕНИЯ ШАБЛОНОВ
    
    Принимает HTML шаблон и данные пользователя, 
    отправляет в OpenAI для персонализации
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        
        if self.api_key and self.api_key != 'your-openai-api-key-here':
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"🤖 [AI SERVICE] OpenAI клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ [AI SERVICE] Ошибка инициализации OpenAI: {str(e)}")
                self.client = None
        else:
            self.client = None
            logger.warning(f"⚠️ [AI SERVICE] OpenAI API ключ не настроен")
    
    def generate_personalized_template(
        self, 
        template: PortfolioTemplate, 
        user_data: str,
        project_title: str,
        project_description: str,
        user: User,
        ai_generation: TemplateAIGeneration
    ) -> Dict[str, Any]:
        """
        🎯 ОСНОВНОЙ МЕТОД AI ЗАПОЛНЕНИЯ ШАБЛОНА
        """
        
        if not self.client:
            return {
                'success': False,
                'error': 'AI сервис недоступен',
                'error_code': 'AI_SERVICE_UNAVAILABLE'
            }
        
        try:
            start_time = time.time()
            
            # Отмечаем начало обработки
            ai_generation.mark_started()
            
            logger.info(f"🤖 [AI FILL] Начинаем заполнение шаблона '{template.title}' для {user.username}")
            
            # Создаем промпт для AI
            ai_prompt = self._build_template_filling_prompt(
                template_html=template.html_code,
                user_data=user_data,
                project_title=project_title,
                project_description=project_description,
                template_title=template.title
            )
            
            logger.info(f"📝 [AI FILL] Промпт создан, длина: {len(ai_prompt)} символов")
            
            # Отправляем запрос к OpenAI
            try:
                ai_response = self._call_openai_api(ai_prompt)
                logger.info("✅ [AI FILL] Получен ответ от OpenAI")
            except Exception as e:
                error_msg = f"Ошибка вызова OpenAI API: {str(e)}"
                logger.error(f"❌ [AI FILL] {error_msg}")
                ai_generation.mark_completed('ai_error', error_message=error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'OPENAI_API_ERROR'
                }
            
            # Парсим и валидируем ответ
            try:
                filled_html = self._parse_ai_response(ai_response)
                logger.info("✅ [AI FILL] HTML успешно извлечен из ответа AI")
            except Exception as e:
                error_msg = f"Ошибка парсинга ответа AI: {str(e)}"
                logger.error(f"❌ [AI FILL] {error_msg}")
                ai_generation.mark_completed('invalid_html', error_message=error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'AI_RESPONSE_PARSE_ERROR'
                }
            
            # Валидируем HTML
            if not self._validate_html(filled_html):
                error_msg = "AI вернул некорректный HTML"
                logger.error(f"❌ [AI FILL] {error_msg}")
                ai_generation.mark_completed('invalid_html', error_message=error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'INVALID_HTML'
                }
            
            # Создаем портфолио на основе заполненного шаблона
            try:
                portfolio = self._create_portfolio_from_filled_template(
                    filled_html=filled_html,
                    original_template=template,
                    project_title=project_title,
                    project_description=project_description,
                    user=user
                )
                logger.info(f"✅ [AI FILL] Портфолио создано: {portfolio.slug}")
            except Exception as e:
                error_msg = f"Ошибка создания портфолио: {str(e)}"
                logger.error(f"❌ [AI FILL] {error_msg}")
                ai_generation.mark_completed('failed', error_message=error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'PORTFOLIO_CREATION_ERROR'
                }
            
            # Завершаем успешно
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            ai_generation.mark_completed(
                status='success',
                portfolio=portfolio,
                generated_html=filled_html
            )
            
            logger.info(f"🎉 [AI FILL] ✅ Успешное заполнение за {response_time}с")
            
            return {
                'success': True,
                'portfolio': portfolio,
                'response_time': response_time,
                'ai_generation_id': ai_generation.id
            }
            
        except Exception as e:
            error_msg = f"Критическая ошибка AI заполнения: {str(e)}"
            logger.error(f"💥 [AI FILL] {error_msg}")
            
            ai_generation.mark_completed('failed', error_message=error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'error_code': 'CRITICAL_ERROR'
            }
    
    def _build_template_filling_prompt(
        self, 
        template_html: str, 
        user_data: str,
        project_title: str,
        project_description: str,
        template_title: str
    ) -> str:
        """
        📝 СОЗДАНИЕ ПРОМПТА ДЛЯ AI ЗАПОЛНЕНИЯ ШАБЛОНА
        """
        
        return f"""Ты - ЭКСПЕРТ по персонализации HTML шаблонов портфолио.

🎯 ЗАДАЧА: Заполни HTML шаблон реальными данными пользователя.

🔥 HTML ШАБЛОН "{template_title}":
{template_html}

👤 ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
{user_data}

📋 ИНФОРМАЦИЯ О ПРОЕКТЕ:
Название: {project_title}
Описание: {project_description}

📝 ИНСТРУКЦИИ:
1. Найди в HTML тексты-плейсхолдеры (Имя, Профессия, О себе, Навыки, Проекты, Контакты и т.д.)
2. Замени их на РЕАЛЬНЫЕ данные пользователя из предоставленной информации
3. Если каких-то данных нет - оставь разумные заглушки или удали секции
4. НЕ меняй структуру HTML, CSS классы или JavaScript
5. Сохрани все теги, атрибуты и форматирование

🚨 ВАЖНО:
- Ответь ТОЛЬКО HTML кодом
- НЕ добавляй markdown блоки ```html
- НЕ добавляй объяснения или комментарии
- Верни ВЕСЬ HTML код с заполненными данными
- HTML должен быть валидным и готовым к использованию

НАЧИНАЙ С <!DOCTYPE html> И ЗАКАНЧИВАЙ </html>"""
    
    def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """
        🔗 ВЫЗОВ OPENAI API
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты - ЭКСПЕРТ по заполнению HTML шаблонов портфолио. 

🎯 ТВОЯ ЗАДАЧА:
- Получить HTML шаблон и данные пользователя
- Найти плейсхолдеры в HTML (имена, профессии, навыки и т.д.)
- Заменить их на реальные данные пользователя
- Вернуть ТОЛЬКО готовый HTML без добавлений

⚡ ПРАВИЛА:
- НЕ меняй структуру HTML
- НЕ удаляй CSS классы
- НЕ добавляй markdown блоки
- Отвечай ТОЛЬКО HTML кодом
- HTML должен быть валидным"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            if not response or not response.choices:
                raise ValueError("Пустой ответ от OpenAI API")
            
            return {
                'content': response.choices[0].message.content,
                'usage': response.usage.dict() if response.usage else {}
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _parse_ai_response(self, ai_response: Dict[str, Any]) -> str:
        """
        🔍 ПАРСИНГ ОТВЕТА AI И ИЗВЛЕЧЕНИЕ HTML
        """
        content = ai_response.get('content', '').strip()
        
        if not content:
            raise ValueError("Пустой контент в ответе AI")
        
        # Удаляем markdown блоки если есть
        if '```html' in content:
            start = content.find('```html') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
            else:
                content = content[start:].strip()
        elif '```' in content:
            # Удаляем любые markdown блоки
            content = re.sub(r'```[\s\S]*?```', '', content).strip()
        
        # Проверяем что HTML начинается правильно
        if not content.startswith('<!DOCTYPE html') and not content.startswith('<html'):
            # Ищем начало HTML в тексте
            html_start = content.find('<!DOCTYPE html')
            if html_start == -1:
                html_start = content.find('<html')
            
            if html_start != -1:
                content = content[html_start:].strip()
            else:
                raise ValueError("HTML не найден в ответе AI")
        
        return content
    
    def _validate_html(self, html_content: str) -> bool:
        """
        ✅ БАЗОВАЯ ВАЛИДАЦИЯ HTML
        """
        if not html_content.strip():
            return False
        
        # Проверяем основные HTML теги
        required_tags = ['<html', '</html>', '<head', '</head>', '<body', '</body>']
        for tag in required_tags:
            if tag not in html_content.lower():
                logger.warning(f"⚠️ [VALIDATION] Отсутствует тег: {tag}")
                return False
        
        # Проверяем что нет явных ошибок
        if 'error' in html_content.lower() or 'ошибка' in html_content.lower():
            return False
        
        # Проверяем минимальную длину
        if len(html_content) < 500:
            logger.warning(f"⚠️ [VALIDATION] HTML слишком короткий: {len(html_content)} символов")
            return False
        
        return True
    
    def _create_portfolio_from_filled_template(
        self,
        filled_html: str,
        original_template: PortfolioTemplate,
        project_title: str,
        project_description: str,
        user: User
    ) -> Portfolio:
        """
        💼 СОЗДАНИЕ ПОРТФОЛИО ИЗ ЗАПОЛНЕННОГО ШАБЛОНА
        """
        
        # Формируем теги для портфолио
        tags = ['ai-generated', 'template-based', original_template.category]
        if original_template.tags:
            tags.extend(original_template.tags[:3])  # Добавляем первые 3 тега шаблона
        
        # Создаем портфолио
        portfolio = Portfolio.objects.create(
            author=user,
            title=project_title,
            description=project_description,
            html_content=filled_html,
            css_content=original_template.css_code,  # Используем CSS шаблона
            js_content=original_template.js_code or '',  # Используем JS шаблона если есть
            tags=tags,
            is_public=False  # По умолчанию приватное
        )
        
        return portfolio
    
    def get_user_ai_stats(self, user: User) -> Dict[str, Any]:
        """
        📊 ПОЛУЧЕНИЕ СТАТИСТИКИ AI ИСПОЛЬЗОВАНИЯ ПОЛЬЗОВАТЕЛЯ
        """
        try:
            # Общая статистика
            total_requests = TemplateAIGeneration.objects.filter(user=user).count()
            successful_requests = TemplateAIGeneration.objects.filter(
                user=user, status='success'
            ).count()
            
            # Статистика за сегодня
            today = timezone.now().date()
            today_stats, _ = TemplateAIStats.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'ai_requests_count': 0,
                    'ai_successful_count': 0,
                    'ai_failed_count': 0,
                    'regular_usage_count': 0
                }
            )
            
            return {
                'total_ai_requests': total_requests,
                'total_ai_successful': successful_requests,
                'success_rate': round((successful_requests / total_requests * 100), 1) if total_requests > 0 else 0,
                'today_requests': today_stats.ai_requests_count,
                'today_successful': today_stats.ai_successful_count,
                'remaining_today': max(0, 10 - today_stats.ai_requests_count),
                'regular_usage_today': today_stats.regular_usage_count
            }
            
        except Exception as e:
            logger.error(f"[AI STATS] Ошибка получения статистики: {str(e)}")
            return {
                'total_ai_requests': 0,
                'total_ai_successful': 0,
                'success_rate': 0,
                'today_requests': 0,
                'today_successful': 0,
                'remaining_today': 10,
                'regular_usage_today': 0
            } 