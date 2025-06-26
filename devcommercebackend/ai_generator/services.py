import json
import time
from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from openai import OpenAI
from portfolio.models import Portfolio
from .models import AIGenerationRequest, AIGenerationStats, GlobalAIStats

# Добавляем импорты для форматирования кода
from bs4 import BeautifulSoup
import cssbeautifier
import jsbeautifier

User = get_user_model()


class AIGenerationService:
    """Сервис для генерации портфолио через AI"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_API_URL
        self.model = settings.DEEPSEEK_MODEL
        self.timeout = getattr(settings, 'AI_GENERATION_TIMEOUT', 30)
        self.max_retries = 1
        
        # Инициализируем OpenAI клиент для DeepSeek
        if self.api_key:
            try:
                print(f"[DEBUG] Инициализация DeepSeek клиента")
                print(f"[DEBUG] API Key: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 10 else '***'}")
                print(f"[DEBUG] Base URL: {self.base_url}")
                print(f"[DEBUG] Model: {self.model}")
                
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                print(f"[DEBUG] DeepSeek клиент успешно инициализирован")
            except Exception as e:
                print(f"[DEBUG] Ошибка инициализации DeepSeek клиента: {str(e)}")
                self.client = None
        else:
            self.client = None
            print(f"[DEBUG] DeepSeek клиент НЕ инициализирован - нет API ключа")
    
    def check_user_limits(self, user: User) -> Tuple[bool, str]:
        """Проверка лимитов пользователя"""
        if not user.is_premium:
            return False, "AI генерация доступна только Premium пользователям"
        
        # Проверяем дневной лимит
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
        
        if stats.requests_count >= 5:
            return False, f"Превышен дневной лимит AI генераций (5/день). Попробуйте завтра."
        
        return True, "OK"
    
    def build_ai_prompt(self, user_prompt: str, style: str = "modern") -> str:
        """Создание структурированного промпта для DeepSeek"""
        
        style_descriptions = {
            'modern': 'современный дизайн с чистыми линиями, градиентами и анимациями',
            'minimal': 'минималистичный дизайн с большим количеством белого пространства',
            'creative': 'креативный и яркий дизайн с необычными элементами',
            'business': 'строгий бизнес стиль с профессиональными цветами',
            'dark': 'темная тема с контрастными элементами',
            'colorful': 'яркий и красочный дизайн с насыщенными цветами'
        }
        
        style_desc = style_descriptions.get(style, 'современный дизайн')
        
        return f"""Ты - эксперт веб-разработчик. Создай полноценный сайт по описанию пользователя.

СТИЛЬ: {style_desc}
ПРОМПТ ПОЛЬЗОВАТЕЛЯ: {user_prompt}

ТРЕБОВАНИЯ:
- Верни ТОЛЬКО валидный JSON без markdown блока
- HTML: чистая семантичная разметка БЕЗ КАРТИНОК (img тегов)
- CSS: адаптивный дизайн с медиа-запросами
- JS: базовая интерактивность
- Код должен быть компактным но функциональным
- НЕ ИСПОЛЬЗУЙ КАРТИНКИ, вместо них используй CSS фигуры, градиенты, иконки символами
- Всегда создавай сайт адаптивным и по больше его делай , он должен быть большим и красивым и должен соотвествовать требованиям пользоватея , ты должен всегда улучшать промпт пользоваетя , ты должен превозходить ожидания пользоваетя !
ОТВЕЧАЙ СТРОГО В ФОРМАТЕ:
{{"html": "полный HTML код", "css": "полный CSS код", "js": "полный JS код"}}
БЕЗ MARKDOWN БЛОКА!"""

    def call_deepseek_api(self, prompt: str) -> Dict[str, Any]:
        """Вызов DeepSeek API через OpenAI клиент"""
        if not self.client:
            raise ValueError("DEEPSEEK_API_KEY не настроен")
        

        
        try:
            response = self.client.chat.completions.create(
                extra_body={},
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Ты профессиональный веб-разработчик. Отвечай ТОЛЬКО валидным JSON БЕЗ markdown блока (без ```json и ```). Начинай ответ сразу с { и заканчивай }."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=8000,
                stream=False
            )
            
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Пустой ответ от DeepSeek API")
            
            content = response.choices[0].message.content
            result = {
                "choices": [
                    {
                        "message": {
                            "content": content
                        }
                    }
                ]
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")
    
    def parse_ai_response(self, api_response: Dict[str, Any]) -> Dict[str, str]:
        """Парсинг ответа от DeepSeek API"""
        try:
            if not api_response:
                raise ValueError("api_response пустой")
                
            if 'choices' not in api_response:
                raise ValueError("Отсутствует ключ 'choices' в ответе API")
                
            if not api_response['choices']:
                raise ValueError("Пустой массив choices в ответе API")
                
            # Извлекаем контент из ответа
            choice = api_response['choices'][0]
            if not choice or 'message' not in choice:
                raise ValueError("Отсутствует message в choices[0]")
                
            message = choice['message']
            if not message or 'content' not in message:
                raise ValueError("Отсутствует content в message")
                
            content = message['content']
            if not content:
                raise ValueError("Пустой контент в ответе API")
            
            # Пытаемся распарсить JSON
            # Ищем JSON в ответе
            if '```json' in content:
                # Обрабатываем markdown блок
                start_idx = content.find('```json') + 7
                end_idx = content.find('```', start_idx)
                if end_idx == -1:
                    # Блок не закрыт, берем до конца
                    json_content = content[start_idx:].strip()
                    # Находим последнюю полную скобку
                    last_brace = json_content.rfind('}')
                    if last_brace != -1:
                        json_content = json_content[:last_brace + 1]
                else:
                    json_content = content[start_idx:end_idx].strip()
            else:
                # Ищем прямо JSON
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("JSON не найден в ответе AI")
                json_content = content[start_idx:end_idx]
            
            try:
                code_data = json.loads(json_content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Ошибка парсинга JSON: {str(e)}")
            
            if not isinstance(code_data, dict):
                raise ValueError(f"JSON должен быть объектом, получен {type(code_data)}")
            
            # Валидация обязательных полей
            required_fields = ['html', 'css', 'js']
            for field in required_fields:
                if field not in code_data:
                    raise ValueError(f"Отсутствует обязательное поле: {field}")
            
            # Базовая валидация HTML
            html_content = code_data['html']
            if not html_content.strip().startswith('<!DOCTYPE html>'):
                raise ValueError("HTML должен начинаться с <!DOCTYPE html>")
            
            return {
                'html': html_content.strip(),
                'css': code_data['css'].strip(),
                'js': code_data['js'].strip()
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Неожиданная структура ответа API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Ошибка обработки ответа AI: {str(e)}")
    
    def create_portfolio_from_ai(self, code_data: Dict[str, str], request_data: Dict[str, Any]) -> Portfolio:
        """Создание портфолио из AI сгенерированного кода"""
        
        # Форматируем код для удобочитаемости
        formatted_code = self.format_code_response(code_data)
        
        # Создаем портфолио с отформатированным кодом
        portfolio = Portfolio.objects.create(
            author=request_data['user'],
            title=request_data['title'],
            description=request_data.get('description', ''),
            html_content=formatted_code.get('html', code_data['html']),
            css_content=formatted_code.get('css', code_data['css']),
            js_content=formatted_code.get('js', code_data['js']),
            tags=request_data.get('tags', ['ai-generated', request_data.get('style', 'modern')]),
            is_public=True  # AI сгенерированные портфолио публичны по умолчанию
        )
        return portfolio
    
    def update_user_stats(self, user: User, status: str, response_time: float = None):
        """Обновление статистики пользователя"""
        today = timezone.now().date()
        stats, created = AIGenerationStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'requests_count': 0,
                'successful_count': 0,
                'failed_count': 0,
                'total_response_time': 0.0,
                'popular_styles': {}
            }
        )
        
        stats.requests_count += 1
        
        if status == 'success':
            stats.successful_count += 1
            if response_time:
                stats.total_response_time += response_time
        else:
            stats.failed_count += 1
        
        stats.save()
    
    def update_global_stats(self, status: str, style: str, response_time: float = None):
        """Обновление глобальной статистики"""
        today = timezone.now().date()
        stats, created = GlobalAIStats.objects.get_or_create(
            date=today,
            defaults={
                'total_requests': 0,
                'total_successful': 0,
                'total_failed': 0,
                'active_users': 0,
                'popular_styles': {},
                'error_distribution': {}
            }
        )
        
        stats.total_requests += 1
        
        if status == 'success':
            stats.total_successful += 1
        else:
            stats.total_failed += 1
        
        # Обновляем популярные стили
        if style:
            if style in stats.popular_styles:
                stats.popular_styles[style] += 1
            else:
                stats.popular_styles[style] = 1
        
        stats.save()
    
    def format_html(self, html_code: str) -> str:
        """Форматирует HTML код для удобочитаемости"""
        try:
            # Создаем BeautifulSoup объект
            soup = BeautifulSoup(html_code, 'html.parser')
            # Возвращаем красиво отформатированный HTML
            return soup.prettify()
        except Exception as e:
            logger.warning(f"HTML formatting failed: {e}")
            # Если форматирование не удалось, возвращаем оригинал
            return html_code

    def format_css(self, css_code: str) -> str:
        """Форматирует CSS код для удобочитаемости"""
        try:
            # Используем cssbeautifier для форматирования
            formatted = cssbeautifier.beautify(css_code, {
                'indent_size': 2,
                'indent_char': ' ',
                'max_preserve_newlines': 2,
                'preserve_newlines': True,
                'keep_array_indentation': False,
                'break_chained_methods': False,
                'indent_scripts': 'normal',
                'brace_style': 'collapse',
                'space_before_conditional': True,
                'unescape_strings': False,
                'jslint_happy': False,
                'end_with_newline': True,
                'wrap_line_length': 0,
                'indent_inner_html': False,
                'comma_first': False,
                'e4x': False,
                'indent_empty_lines': False
            })
            return formatted
        except Exception as e:
            logger.warning(f"CSS formatting failed: {e}")
            return css_code

    def format_js(self, js_code: str) -> str:
        """Форматирует JavaScript код для удобочитаемости"""
        try:
            # Используем jsbeautifier для форматирования
            formatted = jsbeautifier.beautify(js_code, {
                'indent_size': 2,
                'indent_char': ' ',
                'max_preserve_newlines': 2,
                'preserve_newlines': True,
                'keep_array_indentation': False,
                'break_chained_methods': False,
                'indent_scripts': 'normal',
                'brace_style': 'collapse',
                'space_before_conditional': True,
                'unescape_strings': False,
                'jslint_happy': False,
                'end_with_newline': True,
                'wrap_line_length': 0,
                'indent_inner_html': False,
                'comma_first': False,
                'e4x': False,
                'indent_empty_lines': False
            })
            return formatted
        except Exception as e:
            logger.warning(f"JavaScript formatting failed: {e}")
            return js_code

    def format_code_response(self, code_data: Dict[str, str]) -> Dict[str, str]:
        """Форматирует весь код из ответа AI"""
        formatted_code = {}
        
        # Форматируем HTML
        if 'html' in code_data:
            formatted_code['html'] = self.format_html(code_data['html'])
        
        # Форматируем CSS
        if 'css' in code_data:
            formatted_code['css'] = self.format_css(code_data['css'])
        
        # Форматируем JS
        if 'js' in code_data:
            formatted_code['js'] = self.format_js(code_data['js'])
        
        return formatted_code

    def generate_portfolio(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод генерации портфолио"""
        try:
            user = request_data['user']
        except (KeyError, TypeError) as e:
            return {
                'success': False,
                'error': f'Ошибка в request_data: {str(e)}',
                'error_code': 'INVALID_REQUEST'
            }
        
        # Проверяем лимиты
        can_generate, error_message = self.check_user_limits(user)
        if not can_generate:
            return {
                'success': False,
                'error': error_message,
                'error_code': 'LIMIT_EXCEEDED'
            }
        
        # Создаем запись о запросе
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            prompt=request_data['prompt'],
            title=request_data['title'],
            description=request_data.get('description', ''),
            style=request_data.get('style', 'modern'),
            status='processing'
        )
        
        try:
            # Отмечаем начало обработки
            ai_request.mark_started()
            start_time = time.time()
            
            # Создаем промпт
            full_prompt = self.build_ai_prompt(
                request_data['prompt'], 
                request_data.get('style', 'modern')
            )
            
            # Вызываем AI API
            try:
                api_response = self.call_deepseek_api(full_prompt)
                if not api_response:
                    raise ValueError("API вернул None")
                ai_request.ai_raw_response = json.dumps(api_response, ensure_ascii=False)
                ai_request.save()
            except Exception as e:
                raise Exception(f"Ошибка API вызова: {str(e)}")
            
            # Парсим ответ
            try:
                code_data = self.parse_ai_response(api_response)
                if not code_data:
                    raise ValueError("parse_ai_response вернул None")
            except Exception as e:
                raise Exception(f"Ошибка парсинга: {str(e)}")
            
            # Создаем портфолио
            try:
                portfolio = self.create_portfolio_from_ai(code_data, request_data)
                if not portfolio:
                    raise ValueError("create_portfolio_from_ai вернул None")
            except Exception as e:
                raise Exception(f"Ошибка создания портфолио: {str(e)}")
            
            # Вычисляем время ответа
            response_time = time.time() - start_time
            
            # Отмечаем успешное завершение
            ai_request.mark_completed('success', portfolio)
            ai_request.response_time = response_time
            ai_request.save()
            
            # Обновляем статистику
            self.update_user_stats(user, 'success', response_time)
            self.update_global_stats('success', request_data.get('style', 'modern'), response_time)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'request_id': ai_request.id,
                'response_time': response_time
            }
            
        except Exception as e:
            error_msg = f"Ошибка генерации: {str(e)}"
            print(f"[ERROR] {error_msg}")  # Временная отладка
            
            # Проверяем на таймаут (может быть в сообщении об ошибке)
            if 'timeout' in str(e).lower() or 'time' in str(e).lower():
                error_msg = "Превышено время ожидания ответа от AI сервера"
                ai_request.mark_completed('timeout', error_message=error_msg)
                self.update_user_stats(user, 'timeout')
                self.update_global_stats('timeout', request_data.get('style', 'modern'))
                
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'TIMEOUT'
                }
            
        except ValueError as e:
            error_msg = f"Ошибка обработки ответа AI: {str(e)}"
            ai_request.mark_completed('invalid_response', error_message=error_msg)
            self.update_user_stats(user, 'invalid_response')
            self.update_global_stats('invalid_response', request_data.get('style', 'modern'))
            
            return {
                'success': False,
                'error': "AI вернул некорректный код. Попробуйте изменить промпт.",
                'error_code': 'INVALID_RESPONSE'
            }
            
        except Exception as e:
            error_msg = f"Ошибка генерации: {str(e)}"
            ai_request.mark_completed('ai_error', error_message=error_msg)
            self.update_user_stats(user, 'ai_error')
            self.update_global_stats('ai_error', request_data.get('style', 'modern'))
            
            return {
                'success': False,
                'error': "Сервера AI временно перегружены. Попробуйте позже.",
                'error_code': 'AI_ERROR'
            }


# Вспомогательные функции
def sync_generate_portfolio(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Синхронная генерация портфолио"""
    service = AIGenerationService()
    return service.generate_portfolio(request_data) 