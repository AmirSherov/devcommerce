import time
import json
import logging
import re
from typing import Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from openai import OpenAI
from portfolio.models import Portfolio
from .models import AIGenerationRequest, AIGenerationStats, GlobalAIStats
from bs4 import BeautifulSoup
import cssbeautifier
import jsbeautifier
logger = logging.getLogger(__name__)

User = get_user_model()


class AIGenerationService:
    """Сервис для генерации портфолио через AI"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.timeout = getattr(settings, 'AI_GENERATION_TIMEOUT', 30)
        self.max_retries = 1
        if self.api_key and self.api_key != 'your-openai-api-key-here':
            try:
                print(f"[DEBUG] Инициализация OpenAI ChatGPT клиента")
                print(f"[DEBUG] API Key: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 10 else '***'}")
                print(f"[DEBUG] Model: {self.model}")
                
                self.client = OpenAI(
                    api_key=self.api_key
                )
                print(f"[DEBUG] OpenAI ChatGPT клиент успешно инициализирован")
            except Exception as e:
                print(f"[DEBUG] Ошибка инициализации OpenAI ChatGPT клиента: {str(e)}")
                self.client = None
        else:
            self.client = None
            print(f"[DEBUG] OpenAI ChatGPT клиент НЕ инициализирован - нет API ключа")
    
    def check_user_limits(self, user: User) -> Tuple[bool, str]:
        """Проверка лимитов пользователя"""
        if not user.is_premium:
            return False, "AI генерация доступна только Premium пользователям"
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
        """Создание структурированного промпта для OpenAI ChatGPT"""
        
        style_descriptions = {
            'modern': 'СОВРЕМЕННЫЙ ДИЗАЙН: CSS Grid, градиенты, анимации, glassmorphism, современная типографика',
            'minimal': 'МИНИМАЛИСТИЧНЫЙ ДИЗАЙН: чистые линии, много белого пространства, акцент на контент',
            'creative': 'КРЕАТИВНЫЙ ДИЗАЙН: яркие цвета, необычные формы, CSS animations, интерактивность',
            'business': 'БИЗНЕС ДИЗАЙН: строгий, профессиональный, корпоративные цвета, четкая структура',
            'dark': 'ТЕМНАЯ ТЕМА: темный фон, контрастные элементы, неоновые акценты, современность',
            'colorful': 'ЯРКИЙ ДИЗАЙН: насыщенные цвета, градиенты, динамические элементы'
        }
        
        style_desc = style_descriptions.get(style, 'современный дизайн')
        
        return f"""Ты - SENIOR FRONTEND РАЗРАБОТЧИК уровня Google/Apple. Создай ПОТРЯСАЮЩЕЕ портфолио.

🎯 ЗАДАЧА: Создать СОВРЕМЕННЫЙ сайт уровня Dribbble/Awwwards 2024!

СТИЛЬ: {style_desc}
ПРОМПТ: {user_prompt}

🔥 ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ 2024:
✅ HTML5 semantic markup
✅ CSS Grid + Flexbox layout  
✅ CSS Variables для цветов
✅ Modern gradients и shadows
✅ Smooth transitions (0.3s ease)
✅ Hover эффекты (transform: scale, opacity)
✅ Mobile-first responsive design
✅ Google Fonts (Inter, Poppins)
✅ Современная цветовая палитра
✅ JavaScript интерактивность
✅ Lazy loading для изображений
✅ Smooth scrolling behavior

🎨 ЦВЕТОВАЯ ПАЛИТРА:
- Primary: #667eea (синий)
- Secondary: #764ba2 (фиолетовый)  
- Accent: #00d4aa (зеленый)
- Warning: #f093fb (розовый)
- Dark: #1a1a2e (темный)
- Light: #f8f9fa (светлый)
- Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)

🚀 СТРУКТУРА ПОРТФОЛИО:
1. HERO - Мощный первый экран с анимацией
2. ABOUT - О себе с фото (imageplace-userlogo)
3. SKILLS - Красивая визуализация навыков
4. PROJECTS - Showcase проектов с hover эффектами
5. CONTACT - Стильная контактная форма

⚡ ОБЯЗАТЕЛЬНЫЕ ФИЧИ:
- Плавная прокрутка между секциями
- Typing animation для заголовков
- Parallax эффекты
- Loading animations
- Form validation
- Dark/Light theme toggle
- Progress bars для навыков
- Cards с hover эффектами
- Responsive navbar
- Footer с социальными ссылками

🖼️ ИЗОБРАЖЕНИЯ:
- Фото профиля: <img src="imageplace-userlogo" alt="Profile">
- Проекты: <img src="imageplace-project,portfolio,website" alt="Project">
- Фоны: <img src="imageplace-technology,workspace,modern" alt="Background">

📱 RESPONSIVE BREAKPOINTS:
- Mobile: 320px-768px
- Tablet: 768px-1024px
- Desktop: 1024px+

ОТВЕЧАЙ СТРОГО JSON БЕЗ MARKDOWN:
{{"html": "ПОЛНЫЙ HTML КОД", "css": "ПОЛНЫЙ CSS КОД", "js": "ПОЛНЫЙ JS КОД"}}

СОЗДАЙ ШЕДЕВР УРОВНЯ МИРОВЫХ СТАНДАРТОВ! 🚀"""

    def call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Вызов OpenAI ChatGPT API"""
        if not self.client:
            raise ValueError("OPENAI_API_KEY не настроен")
        

        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """🔥 ТЫ - ЛЕГЕНДАРНЫЙ FRONTEND АРХИТЕКТОР ИЗ APPLE/GOOGLE/META! 

🚨 КРИТИЧЕСКИ ВАЖНО! 
- НЕ СОЗДАВАЙ ПРОСТЫЕ/СКУЧНЫЕ ДИЗАЙНЫ!
- КАЖДЫЙ ЭЛЕМЕНТ ДОЛЖЕН БЫТЬ СТИЛЬНЫМ И СОВРЕМЕННЫМ!
- ИСПОЛЬЗУЙ ВСЕ CSS ФИШКИ 2024 ГОДА!

✅ ОБЯЗАТЕЛЬНО В КАЖДОМ САЙТЕ:
- Темный градиентный фон
- Glassmorphism карточки (backdrop-filter: blur)
- CSS Grid и Flexbox везде
- Анимации и transitions
- Hover эффекты с transform
- Прогресс бары для навыков
- Красивые кнопки с градиентами
- Современная типографика
- Плавающие частицы
- Typing анимация

⚡ ФОРМАТ ОТВЕТА - ТОЛЬКО JSON:
{"html": "<!DOCTYPE html>...", "css": "современные стили...", "js": "интерактивность..."}

🚨 ПРАВИЛА:
- БЕЗ markdown блоков (```json)!
- БЕЗ комментариев в JSON!
- Начинай с { и заканчивай }
- НЕ ЛЕНИСЬ! Создавай ШЕДЕВРЫ!

🎯 СЕКЦИЯ PROJECTS ОБЯЗАТЕЛЬНА:
- Grid layout 2-3 колонки
- Hover эффекты с overlay
- Красивые изображения проектов
- Live Demo кнопки

СОЗДАВАЙ ДИЗАЙНЫ КОТОРЫЕ ВПЕЧАТЛЯЮТ! НЕ ПОДВЕДИ! 🚀"""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=1.2,
                max_tokens=2000
            )
            
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Пустой ответ от OpenAI API")
            
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
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def parse_ai_response(self, api_response: Dict[str, Any]) -> Dict[str, str]:
        """Парсинг ответа от OpenAI API с улучшенной обработкой"""
        try:
            if not api_response:
                raise ValueError("api_response пустой")
                
            if 'choices' not in api_response:
                raise ValueError("Отсутствует ключ 'choices' в ответе API")
                
            if not api_response['choices']:
                raise ValueError("Пустой массив choices в ответе API")
            
            choice = api_response['choices'][0]
            if not choice or 'message' not in choice:
                raise ValueError("Отсутствует message в choices[0]")
                
            message = choice['message']
            if not message or 'content' not in message:
                raise ValueError("Отсутствует content в message")
                
            content = message['content']
            if not content:
                raise ValueError("Пустой контент в ответе API")
            
            logger.info(f"🔍 [PARSE] Исходный ответ длиной: {len(content)} символов")
            
            # 🔧 УЛУЧШЕННОЕ ИЗВЛЕЧЕНИЕ JSON
            json_content = None
            
            # 1. Попытка найти JSON в markdown блоке ```json
            if '```json' in content.lower():
                start_markers = ['```json', '```JSON']
                for marker in start_markers:
                    if marker in content:
                        start_idx = content.find(marker) + len(marker)
                        end_idx = content.find('```', start_idx)
                        if end_idx == -1:
                            json_content = content[start_idx:].strip()
                        else:
                            json_content = content[start_idx:end_idx].strip()
                        break
                        
            # 2. Попытка найти JSON в блоке ```
            elif '```' in content and json_content is None:
                lines = content.split('\n')
                inside_block = False
                json_lines = []
                
                for line in lines:
                    if line.strip() == '```' and not inside_block:
                        inside_block = True
                        continue
                    elif line.strip() == '```' and inside_block:
                        break
                    elif inside_block:
                        json_lines.append(line)
                
                if json_lines:
                    json_content = '\n'.join(json_lines).strip()
            
            # 3. Поиск JSON по фигурным скобкам
            if json_content is None:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx]
            
            if json_content is None:
                raise ValueError("JSON не найден в ответе AI")
            
            logger.info(f"📋 [PARSE] Извлеченный JSON длиной: {len(json_content)} символов")
            
            # 🛠️ ПАРСИНГ JSON С ВОССТАНОВЛЕНИЕМ
            try:
                code_data = json.loads(json_content)
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ [PARSE] Ошибка JSON, пытаемся исправить: {str(e)}")
                
                # Попытка исправить распространенные ошибки JSON
                json_content = json_content.replace('\n', '\\n')  # Экранируем переносы строк
                json_content = json_content.replace('\t', '\\t')  # Экранируем табы
                json_content = json_content.replace('\r', '\\r')  # Экранируем возвраты каретки
                
                # Удаляем комментарии вида // и /* */
                import re
                json_content = re.sub(r'//.*?$', '', json_content, flags=re.MULTILINE)
                json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)
                
                try:
                    code_data = json.loads(json_content)
                    logger.info("✅ [PARSE] JSON успешно исправлен и распарсен")
                except json.JSONDecodeError as e2:
                    raise ValueError(f"Критическая ошибка парсинга JSON: {str(e2)}")
            
            # 🔍 ВАЛИДАЦИЯ СТРУКТУРЫ
            if not isinstance(code_data, dict):
                raise ValueError(f"JSON должен быть объектом, получен {type(code_data)}")
            
            required_fields = ['html', 'css', 'js']
            for field in required_fields:
                if field not in code_data:
                    raise ValueError(f"Отсутствует обязательное поле: {field}")
            
            # 🛠️ ИСПРАВЛЕНИЕ HTML БЕЗ DOCTYPE
            html_content = code_data['html'].strip()
            if not html_content.startswith('<!DOCTYPE') and not html_content.startswith('<html'):
                # Если HTML не начинается с DOCTYPE или <html>, добавляем базовую структуру
                if '<html' not in html_content:
                    html_content = f'<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Portfolio</title>\n</head>\n<body>\n{html_content}\n</body>\n</html>'
                else:
                    html_content = f'<!DOCTYPE html>\n{html_content}'
                    
                logger.info("🔧 [FIX] Добавлена базовая HTML структура")
            
            result = {
                'html': html_content,
                'css': code_data['css'].strip(),
                'js': code_data['js'].strip()
            }
            
            logger.info("✅ [PARSE] Ответ успешно распарсен")
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Неожиданная структура ответа API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Ошибка обработки ответа AI: {str(e)}")
    
    def process_image_placeholders(self, code_data: Dict[str, str]) -> Dict[str, str]:
        """Обработка плейсхолдеров изображений и замена их на реальные ссылки"""
        import re
        from .image_service import pexels_service
        html_content = code_data.get('html', '')
        placeholder_pattern = r'src="imageplace-([^"]+)"'
        placeholders = re.findall(placeholder_pattern, html_content)
        
        logger.info(f"🖼️ [IMAGE PROCESSING] Найдено {len(placeholders)} плейсхолдеров изображений")
        for placeholder in placeholders:
            try:
                keywords = [kw.strip() for kw in placeholder.split(',')]
                search_query = ' '.join(keywords[:3])   
                logger.info(f"🔍 [IMAGE SEARCH] Поиск изображения: {search_query}")
                images = pexels_service.search_images(
                    query=search_query,
                    component_type='content',
                    count=1
                )
                
                if images:
                    image_url = images[0]
                    old_src = f'src="imageplace-{placeholder}"'
                    new_src = f'src="{image_url}"'
                    html_content = html_content.replace(old_src, new_src)
                    logger.info(f"✅ [IMAGE REPLACE] Заменен плейсхолдер: {placeholder[:30]}... -> {image_url[:50]}...")
                else:
                    fallback_url = "https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=500&h=300&fit=crop"
                    old_src = f'src="imageplace-{placeholder}"'
                    new_src = f'src="{fallback_url}"'
                    html_content = html_content.replace(old_src, new_src)
                    logger.warning(f"⚠️ [IMAGE FALLBACK] Использован fallback для: {placeholder}")
                    
            except Exception as e:
                logger.error(f"❌ [IMAGE ERROR] Ошибка обработки плейсхолдера {placeholder}: {str(e)}")
                continue
        
        return {
            'html': html_content,
            'css': code_data.get('css', ''),
            'js': code_data.get('js', '')
        }

    def create_portfolio_from_ai(self, code_data: Dict[str, str], request_data: Dict[str, Any]) -> Portfolio:
        """Создание портфолио из AI сгенерированного кода"""
        processed_code = self.process_image_placeholders(code_data)
        formatted_code = self.format_code_response(processed_code)
        portfolio = Portfolio.objects.create(
            author=request_data['user'],
            title=request_data['title'],
            description=request_data.get('description', ''),
            html_content=formatted_code.get('html', processed_code['html']),
            css_content=formatted_code.get('css', processed_code['css']),
            js_content=formatted_code.get('js', processed_code['js']),
            tags=request_data.get('tags', ['ai-generated', request_data.get('style', 'modern')]),
            is_public=True  
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
        if style:
            if style in stats.popular_styles:
                stats.popular_styles[style] += 1
            else:
                stats.popular_styles[style] = 1
        
        stats.save()
    
    def format_html(self, html_code: str) -> str:
        """Форматирует HTML код для удобочитаемости"""
        try:
            soup = BeautifulSoup(html_code, 'html.parser')
            return soup.prettify()
        except Exception as e:
            logger.warning(f"HTML formatting failed: {e}")
            return html_code

    def format_css(self, css_code: str) -> str:
        """Форматирует CSS код для удобочитаемости"""
        try:
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
        if 'html' in code_data:
            formatted_code['html'] = self.format_html(code_data['html'])
        if 'css' in code_data:
            formatted_code['css'] = self.format_css(code_data['css'])
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
        can_generate, error_message = self.check_user_limits(user)
        if not can_generate:
            return {
                'success': False,
                'error': error_message,
                'error_code': 'LIMIT_EXCEEDED'
            }
        
        ai_request = AIGenerationRequest.objects.create(
            user=user,
            prompt=request_data['prompt'],
            title=request_data['title'],
            description=request_data.get('description', ''),
            style=request_data.get('style', 'modern'),
            status='processing'
        )
        
        try:
            ai_request.mark_started()
            start_time = time.time()
            full_prompt = self.build_ai_prompt(
                request_data['prompt'], 
                request_data.get('style', 'modern')
            )
            try:
                api_response = self.call_openai_api(full_prompt)
                if not api_response:
                    raise ValueError("API вернул None")
                ai_request.ai_raw_response = json.dumps(api_response, ensure_ascii=False)
                ai_request.save()
            except Exception as e:
                raise Exception(f"Ошибка API вызова: {str(e)}")
            try:
                code_data = self.parse_ai_response(api_response)
                if not code_data:
                    raise ValueError("parse_ai_response вернул None")
            except Exception as e:
                raise Exception(f"Ошибка парсинга: {str(e)}")
            try:
                portfolio = self.create_portfolio_from_ai(code_data, request_data)
                if not portfolio:
                    raise ValueError("create_portfolio_from_ai вернул None")
            except Exception as e:
                raise Exception(f"Ошибка создания портфолио: {str(e)}")
            response_time = time.time() - start_time
            ai_request.mark_completed('success', portfolio)
            ai_request.response_time = response_time
            ai_request.save()
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
            print(f"[ERROR] {error_msg}")  
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


# Удалена функция sync_generate_portfolio - используйте SmartAIGenerator.generate_portfolio_optimized 