import time
import logging
import json
from typing import Dict, Any, List, Tuple
from .models import AIGenerationRequest
from .services import AIGenerationService
from .image_service import pexels_service

logger = logging.getLogger(__name__)


class PremiumSmartAIGenerator:
    """
    🚀 РЕВОЛЮЦИОННЫЙ AI ГЕНЕРАТОР САЙТОВ МИРОВОГО УРОВНЯ!
    
    7-шаговый процесс создания уникальных сайтов:
    1. Бизнес-анализ и стратегия
    2. Архитектура и UX планирование  
    3. Дизайн-концепция и стиль
    4. Контент-стратегия и копирайтинг
    5. Медиа и автоматические изображения
    6. Интерактивность и анимации
    7. Финальная сборка и оптимизация
    """
    
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.image_service = pexels_service
        logger.info("🔥 [PREMIUM AI] Инициализация РЕВОЛЮЦИОННОГО генератора мирового уровня!")
        
        # Мастер-промпты для каждого этапа
        self.step_prompts = {
            1: self._get_business_analysis_prompt,
            2: self._get_architecture_prompt,
            3: self._get_design_concept_prompt,
            4: self._get_content_strategy_prompt,
            5: self._get_media_integration_prompt,
            6: self._get_interactivity_prompt,
            7: self._get_final_assembly_prompt
        }

    def generate_website_premium(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 ПРЕМИУМ ГЕНЕРАЦИЯ САЙТА - 7 ШАГОВ К СОВЕРШЕНСТВУ!
        
        Args:
            request_data: Расширенные данные пользователя
            
        Returns:
            Результат премиум генерации
        """
        logger.info(f"🚀 [PREMIUM] Запуск РЕВОЛЮЦИОННОЙ генерации для: {request_data.get('user', 'Unknown')}")
        
        try:
            # Создаем контекст проекта
            project_context = self._analyze_project_context(request_data)
            logger.info(f"📊 [STEP 0] Контекст проекта создан: {project_context['industry']} / {project_context['style']}")
            
            # Выполняем 7 шагов премиум генерации
            generation_steps = {}
            for step in range(1, 8):
                logger.info(f"⚡ [STEP {step}/7] Начинаем: {self._get_step_name(step)}")
                
                step_result = self._execute_generation_step(
                    step=step,
                    project_context=project_context,
                    previous_steps=generation_steps,
                    request_data=request_data
                )
                
                generation_steps[step] = step_result
                logger.info(f"✅ [STEP {step}/7] Завершён: {self._get_step_name(step)}")
                
                # Небольшая пауза между шагами для качества
                time.sleep(0.5)
            
            # Финальная сборка всех этапов в готовый сайт
            final_result = self._assemble_final_website(
                project_context=project_context,
                generation_steps=generation_steps,
                request_data=request_data
            )
            
            logger.info("🎉 [PREMIUM] ШЕДЕВР СОЗДАН! Генерация завершена успешно!")
            return final_result
            
        except Exception as e:
            logger.error(f"💥 [PREMIUM ERROR] Ошибка в премиум генерации: {str(e)}")
            # Fallback на обычную генерацию
            return self._fallback_generation(request_data)

    def _analyze_project_context(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 Анализ контекста проекта"""
        
        user_prompt = request_data.get('prompt', '')
        title = request_data.get('title', '')
        industry = request_data.get('industry', 'general')
        style = request_data.get('style', 'modern')
        
        # Определяем тип бизнеса из промпта
        business_type = self._detect_business_type(user_prompt, title)
        
        # Извлекаем ключевые слова для изображений
        image_keywords = self._extract_image_keywords(user_prompt, business_type)
        
        return {
            'user_prompt': user_prompt,
            'title': title,
            'industry': industry,
            'style': style,
            'business_type': business_type,
            'image_keywords': image_keywords,
            'target_audience': self._detect_target_audience(user_prompt),
            'primary_goals': self._detect_primary_goals(user_prompt),
            'unique_selling_points': self._extract_usp(user_prompt)
        }

    def _execute_generation_step(self, step: int, project_context: Dict, previous_steps: Dict, request_data: Dict) -> Dict[str, Any]:
        """⚡ Выполнение конкретного шага генерации"""
        
        # Получаем промпт для текущего шага
        prompt_generator = self.step_prompts[step]
        step_prompt = prompt_generator(project_context, previous_steps)
        
        # Логируем промпт для отладки (первые 200 символов)
        logger.info(f"🎯 [STEP {step}] Промпт: {step_prompt[:200]}...")
        
        try:
            # Вызываем AI для текущего шага
            ai_response = self.ai_service.call_deepseek_api(step_prompt)
            
            logger.info(f"🔍 [STEP {step}] AI Response type: {type(ai_response)}")
            logger.info(f"🔍 [STEP {step}] AI Response keys: {list(ai_response.keys()) if isinstance(ai_response, dict) else 'not a dict'}")
            
            if not ai_response:
                raise ValueError(f"Пустой ответ AI на шаге {step}")
            
            # Парсим ответ в зависимости от шага
            parsed_result = self._parse_step_response(step, ai_response, project_context)
            
            logger.info(f"🔍 [STEP {step}] Parsed result type: {type(parsed_result)}")
            logger.info(f"🔍 [STEP {step}] Parsed result keys: {list(parsed_result.keys()) if isinstance(parsed_result, dict) else 'not a dict'}")
            
            # Специальная проверка для шага 7 (финальный код)
            if step == 7:
                logger.info(f"🔍 [STEP 7] Final code check:")
                logger.info(f"  - Has 'html': {'html' in parsed_result}")
                logger.info(f"  - Has 'css': {'css' in parsed_result}")
                logger.info(f"  - Has 'js': {'js' in parsed_result}")
                if 'html' in parsed_result:
                    logger.info(f"  - HTML length: {len(parsed_result.get('html', ''))}")
                if 'css' in parsed_result:
                    logger.info(f"  - CSS length: {len(parsed_result.get('css', ''))}")
            
            return {
                'success': True,
                'step': step,
                'step_name': self._get_step_name(step),
                'result': parsed_result,
                'execution_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ [STEP {step}] Ошибка: {str(e)}")
            return {
                'success': False,
                'step': step,
                'error': str(e)
            }

    def _get_business_analysis_prompt(self, context: Dict, previous: Dict) -> str:
        """📊 Промпт для бизнес-анализа (Шаг 1)"""
        return f"""
Ты - топ бизнес-аналитик и стратег digital агентства. Твоя задача - провести глубокий анализ бизнеса клиента.

ПРОЕКТ: {context['title']}
ОПИСАНИЕ: {context['user_prompt']}
ИНДУСТРИЯ: {context['industry']}

Проведи ПРОФЕССИОНАЛЬНЫЙ анализ и верни результат в JSON формате:

{{
  "business_analysis": {{
    "industry_insights": "глубокий анализ индустрии и трендов",
    "target_audience": "детальный портрет целевой аудитории",
    "competitive_advantages": "уникальные преимущества бизнеса",
    "key_challenges": "основные вызовы индустрии",
    "market_positioning": "позиционирование на рынке",
    "conversion_goals": ["основная цель 1", "цель 2", "цель 3"],
    "success_metrics": "метрики успеха проекта"
  }}
}}

ТРЕБОВАНИЯ:
- Анализ уровня McKinsey & Company
- Конкретные инсайты, не общие фразы
- Фокус на цифровой стратегии
- Учет современных трендов 2024
"""

    def _get_architecture_prompt(self, context: Dict, previous: Dict) -> str:
        """🏗️ Промпт для архитектуры (Шаг 2)"""
        business_data = previous.get(1, {}).get('result', {})
        
        return f"""
Ты - Lead UX Architect в топ-агентстве. Создай информационную архитектуру сайта на основе бизнес-анализа.

БИЗНЕС-АНАЛИЗ: {json.dumps(business_data, ensure_ascii=False)}
ПРОЕКТ: {context['title']} - {context['user_prompt']}

Создай АРХИТЕКТУРУ МИРОВОГО УРОВНЯ в JSON:

{{
  "site_architecture": {{
    "page_structure": {{
      "header": ["элемент 1", "элемент 2"],
      "main_sections": [
        {{"name": "Hero", "purpose": "цель секции", "priority": 1}},
        {{"name": "About", "purpose": "цель", "priority": 2}}
      ],
      "footer": ["элемент 1", "элемент 2"]
    }},
    "user_journey": {{
      "primary_path": "пошаговый путь основного пользователя",
      "secondary_paths": ["альтернативный путь 1", "путь 2"],
      "conversion_points": ["точка конверсии 1", "точка 2"]
    }},
    "navigation_strategy": "стратегия навигации",
    "content_hierarchy": "иерархия контента"
  }}
}}

ПРИНЦИПЫ:
- Фокус на конверсию
- Интуитивная навигация
- Мобильность в приоритете
- Минимум кликов до цели
"""

    def _get_design_concept_prompt(self, context: Dict, previous: Dict) -> str:
        """🎨 Промпт для дизайн-концепции (Шаг 3)"""
        business_data = previous.get(1, {}).get('result', {})
        architecture_data = previous.get(2, {}).get('result', {})
        
        return f"""
Ты - Creative Director уровня Pentagram. Создай уникальную дизайн-концепцию для проекта.

КОНТЕКСТ:
- Бизнес: {json.dumps(business_data, ensure_ascii=False)[:500]}
- Архитектура: {json.dumps(architecture_data, ensure_ascii=False)[:500]}
- Стиль: {context['style']}
- Индустрия: {context['industry']}

Создай ДИЗАЙН-КОНЦЕПЦИЮ AWWWARDS УРОВНЯ в JSON:

{{
  "design_concept": {{
    "visual_identity": {{
      "mood": "настроение дизайна (3-4 слова)",
      "personality": "характер бренда",
      "visual_metaphor": "визуальная метафора"
    }},
    "color_palette": {{
      "primary": "#hex",
      "secondary": "#hex", 
      "accent": "#hex",
      "background": "#hex",
      "text": "#hex"
    }},
    "typography": {{
      "headings": "название шрифта для заголовков",
      "body": "шрифт для текста",
      "accent": "акцентный шрифт"
    }},
    "layout_principles": {{
      "grid_system": "описание сетки",
      "spacing_rhythm": "ритм отступов",
      "visual_hierarchy": "принципы иерархии"
    }},
    "unique_features": ["уникальная фича 1", "фича 2", "фича 3"]
  }}
}}

ТРЕБОВАНИЯ:
- НЕ используй клише и шаблоны
- Создай УНИКАЛЬНУЮ концепцию
- Учти психологию цвета
- Современные тренды 2024
"""

    def _get_content_strategy_prompt(self, context: Dict, previous: Dict) -> str:
        """✍️ Промпт для контент-стратегии (Шаг 4)"""
        design_data = previous.get(3, {}).get('result', {})
        
        return f"""
Ты - топ копирайтер агентства David Ogilvy. Создай убедительную контент-стратегию.

ДИЗАЙН-КОНЦЕПЦИЯ: {json.dumps(design_data, ensure_ascii=False)[:500]}
ПРОЕКТ: {context['title']} - {context['user_prompt']}
АУДИТОРИЯ: {context.get('target_audience', 'широкая')}

Создай КОНТЕНТ МИРОВОГО УРОВНЯ в JSON:

{{
  "content_strategy": {{
    "brand_voice": {{
      "tone": "тон коммуникации",
      "personality": "характер бренда",
      "key_messages": ["ключевое сообщение 1", "сообщение 2", "сообщение 3"]
    }},
    "hero_section": {{
      "headline": "убедительный заголовок",
      "subheadline": "поддерживающий подзаголовок", 
      "cta_text": "призыв к действию",
      "value_proposition": "уникальное ценностное предложение"
    }},
    "content_sections": [
      {{
        "section_name": "название секции",
        "headline": "заголовок секции",
        "content": "основной текст",
        "cta": "призыв к действию"
      }}
    ],
    "seo_keywords": ["ключевое слово 1", "слово 2", "слово 3"],
    "micro_copy": {{
      "buttons": ["текст кнопки 1", "кнопки 2"],
      "form_labels": ["label 1", "label 2"],
      "error_messages": ["сообщение 1", "сообщение 2"]
    }}
  }}
}}

ПРИНЦИПЫ:
- Эмоциональное воздействие
- Конкретные выгоды клиента  
- Социальное доказательство
- Срочность и редкость
"""

    def _get_media_integration_prompt(self, context: Dict, previous: Dict) -> str:
        """🖼️ Промпт для медиа интеграции (Шаг 5)"""
        return f"""
Ты - Art Director топ-агентства. Определи стратегию использования изображений и медиа.

КОНТЕКСТ: {context['title']} - {context['business_type']}
СТИЛЬ: {context['style']}
КЛЮЧЕВЫЕ СЛОВА: {context['image_keywords']}

Создай МЕДИА-СТРАТЕГИЮ в JSON:

{{
  "media_strategy": {{
    "hero_image": {{
      "type": "тип изображения",
      "mood": "настроение",
      "search_query": "поисковый запрос для Pexels",
      "style_notes": "стилевые заметки"
    }},
    "section_images": [
      {{
        "section": "название секции",
        "image_type": "тип изображения",
        "search_query": "запрос для поиска",
        "placement": "размещение изображения"
      }}
    ],
    "image_treatment": {{
      "filters": "фильтры и обработка",
      "overlay": "наложения и эффекты",
      "aspect_ratios": "пропорции изображений"
    }},
    "visual_hierarchy": "иерархия визуальных элементов"
  }}
}}

ТРЕБОВАНИЯ:
- Высокое качество изображений
- Соответствие бренду
- Эмоциональное воздействие
- Поддержка конверсии
"""

    def _get_interactivity_prompt(self, context: Dict, previous: Dict) -> str:
        """⚡ Промпт для интерактивности (Шаг 6)"""
        return f"""
Ты - Lead Frontend Developer топ-агентства. Добавь современную интерактивность.

ПРОЕКТ: {context['title']} - {context['style']}

Создай ИНТЕРАКТИВНОСТЬ ПРЕМИУМ УРОВНЯ в JSON:

{{
  "interactivity": {{
    "animations": {{
      "entrance_effects": ["эффект входа 1", "эффект 2"],
      "scroll_triggers": ["триггер 1", "триггер 2"],
      "hover_effects": ["hover эффект 1", "эффект 2"],
      "loading_animations": "анимация загрузки"
    }},
    "micro_interactions": [
      {{
        "element": "элемент",
        "trigger": "триггер",
        "effect": "эффект",
        "duration": "длительность"
      }}
    ],
    "form_enhancements": {{
      "validation": "валидация в реальном времени",
      "feedback": "обратная связь пользователю",
      "success_states": "состояния успеха"
    }},
    "navigation_effects": "эффекты навигации",
    "scroll_behavior": "поведение при скролле"
  }}
}}

ПРИНЦИПЫ:
- Плавность и естественность
- Обратная связь пользователю
- Производительность
- Доступность
"""

    def _get_final_assembly_prompt(self, context: Dict, previous: Dict) -> str:
        """🎯 Промпт для финальной сборки (Шаг 7)"""
        all_data = {
            'business': previous.get(1, {}).get('result', {}),
            'architecture': previous.get(2, {}).get('result', {}),
            'design': previous.get(3, {}).get('result', {}),
            'content': previous.get(4, {}).get('result', {}),
            'media': previous.get(5, {}).get('result', {}),
            'interactivity': previous.get(6, {}).get('result', {})
        }
        
        return f"""
Ты - Senior Full-Stack Developer агентства уровня IDEO. Собери все элементы в готовый сайт.

ВСЕ ЭТАПЫ ПРОЕКТА:
{json.dumps(all_data, ensure_ascii=False, indent=2)[:3000]}

НАЗВАНИЕ: {context['title']}
СТИЛЬ: {context['style']}

Создай ГОТОВЫЙ САЙТ МИРОВОГО УРОВНЯ с HTML, CSS и JavaScript:

ТРЕБОВАНИЯ К КОДУ:
- Семантичная HTML разметка
- Современный CSS (Grid, Flexbox, Custom Properties)
- Плавные анимации и переходы
- Полная адаптивность (mobile-first)
- Оптимизированная производительность
- Чистый, читаемый код

ВАЖНО ДЛЯ ИЗОБРАЖЕНИЙ:
- Используй img теги там, где нужны изображения
- В src="" пиши специальный плейсхолдер в формате: "imageplace-KEYWORDS"
- Где KEYWORDS - это ключевые слова для поиска изображения через запятую
- Примеры для контекста "{context['business_type']}":
  * <img src="imageplace-{context['business_type']},professional,modern" alt="Главное изображение">
  * <img src="imageplace-{context['business_type']},service,quality" alt="Услуги">
  * <img src="imageplace-team,people,professional" alt="Команда">
  * <img src="imageplace-{context['business_type']},work,process" alt="Процесс работы">
- НЕ используй background-image в CSS для основных изображений контента
- Плейсхолдеры будут автоматически заменены на реальные изображения

ВЕРНИ СТРОГО В ФОРМАТЕ JSON:
{{
  "html": "полный HTML код",
  "css": "полный CSS код", 
  "js": "полный JavaScript код"
}}

СОЗДАЙ ШЕДЕВР УРОВНЯ AWWWARDS! НЕ ИСПОЛЬЗУЙ ШАБЛОНЫ!
"""

    def _assemble_final_website(self, project_context: Dict, generation_steps: Dict, request_data: Dict) -> Dict[str, Any]:
        """🎯 Финальная сборка сайта со всеми элементами"""
        
        try:
            # Получаем финальный код от 7-го шага
            final_step = generation_steps.get(7, {})
            logger.info(f"🔍 [ASSEMBLY] Final step data: {final_step}")
            
            if not final_step.get('success'):
                logger.warning("⚠️ [ASSEMBLY] 7-й шаг не успешен, используем fallback")
                raise ValueError("Ошибка на финальном шаге генерации")
            
            # Парсим код из AI ответа
            code_data = final_step.get('result', {})
            logger.info(f"🔍 [ASSEMBLY] Code data keys: {code_data.keys() if code_data else 'EMPTY'}")
            
            if code_data.get('error'):
                logger.warning("⚠️ [ASSEMBLY] Результат содержит ошибку, используем fallback")
                raise ValueError("AI ответ содержит ошибку")
            
            if code_data:
                logger.info(f"🔍 [ASSEMBLY] HTML length: {len(code_data.get('html', ''))}")
                logger.info(f"🔍 [ASSEMBLY] CSS length: {len(code_data.get('css', ''))}")
                logger.info(f"🔍 [ASSEMBLY] JS length: {len(code_data.get('js', ''))}")
            
            if not code_data:
                logger.warning("⚠️ [ASSEMBLY] Пустой результат, используем fallback")
                raise ValueError("Пустой результат финального шага")
            
            # Проверяем наличие кода
            if not code_data.get('html') and not code_data.get('css'):
                logger.warning("⚠️ [ASSEMBLY] Пустой HTML и CSS, используем fallback")
                logger.error(f"❌ [ASSEMBLY] Raw result: {str(final_step.get('result'))[:500]}")
                raise ValueError("AI не сгенерировал HTML/CSS код")
            
            # Интегрируем изображения в код
            enhanced_code = self._integrate_images_into_code(code_data, generation_steps, project_context)
            
            logger.info(f"🔍 [ASSEMBLY] Enhanced HTML length: {len(enhanced_code.get('html', ''))}")
            logger.info(f"🔍 [ASSEMBLY] Enhanced CSS length: {len(enhanced_code.get('css', ''))}")
            
            # Создаем портфолио с улучшенным кодом
            portfolio = self.ai_service.create_portfolio_from_ai(enhanced_code, request_data)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'generation_steps': len(generation_steps),
                'project_context': project_context,
                'enhanced_features': self._get_enhancement_summary(generation_steps)
            }
            
        except Exception as e:
            logger.error(f"💥 [ASSEMBLY ERROR] Ошибка финальной сборки: {str(e)}")
            
            # Используем fallback генерацию
            try:
                logger.info("🔄 [ASSEMBLY FALLBACK] Переключение на обычную генерацию")
                fallback_result = self.ai_service.generate_portfolio(request_data)
                
                if fallback_result.get('success'):
                    return {
                        'success': True,
                        'portfolio': fallback_result['portfolio'],
                        'generation_steps': 1,  # Обычная генерация = 1 шаг
                        'project_context': project_context,
                        'enhanced_features': ['✅ Fallback генерация', '🖼️ Автоматические изображения'],
                        'fallback_used': True
                    }
                else:
                    raise Exception(f"Fallback генерация тоже не удалась: {fallback_result.get('error')}")
                    
            except Exception as fallback_error:
                logger.error(f"💥 [FALLBACK ERROR] {str(fallback_error)}")
                raise Exception(f"Критическая ошибка: {str(e)}. Fallback: {str(fallback_error)}")

    def _integrate_images_into_code(self, code_data: Dict, generation_steps: Dict, context: Dict) -> Dict[str, str]:
        """🖼️ Автоматическая интеграция изображений в код"""
        
        try:
            # Теперь обработка изображений происходит через плейсхолдеры в AIGenerationService
            # Здесь мы просто добавляем дополнительные background изображения через CSS
            
            html_code = code_data.get('html', '')
            css_code = code_data.get('css', '')
            
            # Получаем медиа-стратегию из 5-го шага для background изображений
            media_step = generation_steps.get(5, {}).get('result', {})
            media_strategy = media_step.get('media_strategy', {})
            
            # Добавляем hero background изображение
            hero_image = self._get_hero_image(media_strategy, context)
            if hero_image:
                css_code = self._inject_hero_image_css(css_code, hero_image)
                logger.info(f"🖼️ [BACKGROUND] Hero background добавлен: {hero_image[:50]}...")
            
            # Добавляем section background изображения
            section_images = self._get_section_images(media_strategy, context)
            if section_images:
                css_code = self._inject_section_images_css(css_code, section_images)
                logger.info(f"🖼️ [BACKGROUND] Добавлено {len(section_images)} background изображений")
            
            return {
                'html': html_code,
                'css': css_code,
                'js': code_data.get('js', '')
            }
            
        except Exception as e:
            logger.error(f"❌ [IMAGES] Ошибка интеграции изображений: {str(e)}")
            # Возвращаем код без дополнительных изображений
            return code_data

    def _get_hero_image(self, media_strategy: Dict, context: Dict) -> str:
        """Получение главного изображения"""
        try:
            hero_info = media_strategy.get('hero_image', {})
            search_query = hero_info.get('search_query', '') or f"{context['business_type']} professional modern"
            
            images = self.image_service.search_images(
                query=search_query,
                component_type='hero',
                count=1
            )
            
            return images[0] if images else None
            
        except Exception as e:
            logger.error(f"❌ Hero image error: {str(e)}")
            return None

    def _get_section_images(self, media_strategy: Dict, context: Dict) -> List[str]:
        """Получение изображений для секций"""
        try:
            section_images = []
            sections = media_strategy.get('section_images', [])
            
            for section_info in sections[:3]:  # Максимум 3 изображения
                search_query = section_info.get('search_query', '') or f"{context['business_type']} service"
                
                images = self.image_service.search_images(
                    query=search_query,
                    component_type='features',
                    count=1
                )
                
                if images:
                    section_images.extend(images)
            
            return section_images
            
        except Exception as e:
            logger.error(f"❌ Section images error: {str(e)}")
            return []

    def _inject_hero_image_css(self, css_code: str, image_url: str) -> str:
        """Добавление hero изображения в CSS"""
        hero_css = f"""
/* AI Generated Hero Background */
.hero, .hero-section, section:first-of-type, .banner, .intro {{
    background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('{image_url}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
"""
        return css_code + hero_css

    def _inject_section_images_css(self, css_code: str, images: List[str]) -> str:
        """Добавление изображений секций в CSS"""
        section_css = ""
        
        for i, image_url in enumerate(images):
            section_css += f"""
/* AI Generated Section Image {i+1} */
.section-{i+1}, .feature-{i+1}, .service-{i+1} {{
    background-image: url('{image_url}');
    background-size: cover;
    background-position: center;
}}
"""
        
        return css_code + section_css

    # Вспомогательные методы
    def _detect_business_type(self, prompt: str, title: str) -> str:
        """Определение типа бизнеса из промпта"""
        text = (prompt + " " + title).lower()
        
        if any(word in text for word in ['ресторан', 'кафе', 'пиццер', 'суши', 'бар', 'food']):
            return 'restaurant'
        elif any(word in text for word in ['it', 'tech', 'software', 'app', 'digital']):
            return 'technology'
        elif any(word in text for word in ['врач', 'медицин', 'клиника', 'health']):
            return 'healthcare'
        elif any(word in text for word in ['фитнес', 'спорт', 'gym', 'fitness']):
            return 'fitness'
        else:
            return 'business'

    def _extract_image_keywords(self, prompt: str, business_type: str) -> List[str]:
        """Извлечение ключевых слов для поиска изображений"""
        base_keywords = {
            'restaurant': ['food', 'dining', 'restaurant interior', 'chef cooking'],
            'technology': ['technology', 'modern office', 'computer', 'innovation'],
            'healthcare': ['medical', 'healthcare', 'doctor', 'clinic'],
            'fitness': ['fitness', 'gym', 'workout', 'health'],
            'business': ['business', 'office', 'professional', 'corporate']
        }
        
        return base_keywords.get(business_type, ['professional', 'modern', 'quality'])

    def _get_step_name(self, step: int) -> str:
        """Получение названия шага"""
        step_names = {
            1: "Бизнес-анализ и стратегия",
            2: "Архитектура и UX планирование", 
            3: "Дизайн-концепция и стиль",
            4: "Контент-стратегия и копирайтинг",
            5: "Медиа и изображения",
            6: "Интерактивность и анимации",
            7: "Финальная сборка и оптимизация"
        }
        return step_names.get(step, f"Шаг {step}")

    def _parse_step_response(self, step: int, ai_response: Dict, context: Dict) -> Dict:
        """Парсинг ответа AI для конкретного шага"""
        try:
            # Логируем входные данные
            logger.info(f"🔍 [PARSE STEP {step}] Response type: {type(ai_response)}")
            
            # Если ответ уже в формате Dict, используем его
            if isinstance(ai_response, dict):
                # Проверяем структуру ответа DeepSeek
                if 'choices' in ai_response and ai_response['choices']:
                    content = ai_response['choices'][0].get('message', {}).get('content', '')
                    logger.info(f"🔍 [PARSE STEP {step}] Found content in choices, length: {len(content)}")
                    text = content
                else:
                    logger.info(f"🔍 [PARSE STEP {step}] Using dict as is")
                    return ai_response
            else:
                text = str(ai_response)
                
            # Ищем начало и конец JSON
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            logger.info(f"🔍 [PARSE STEP {step}] JSON boundaries: start={start_idx}, end={end_idx}")
            
            if start_idx == -1 or end_idx == 0:
                logger.error(f"❌ [PARSE STEP {step}] JSON not found. First 500 chars: {text[:500]}")
                raise ValueError(f"JSON не найден в ответе AI на шаге {step}")
                
            json_str = text[start_idx:end_idx]
            logger.info(f"🔍 [PARSE STEP {step}] Extracted JSON length: {len(json_str)}")
            
            # Пытаемся распарсить JSON
            try:
                result = json.loads(json_str)
                logger.info(f"✅ [PARSE STEP {step}] Successfully parsed JSON with keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"❌ Parse error step {step}: {str(e)}")
                logger.error(f"❌ [PARSE STEP {step}] JSON string first 200 chars: {json_str[:200]}")
                logger.error(f"❌ [PARSE STEP {step}] JSON string last 200 chars: {json_str[-200:]}")
                
                # Пытаемся исправить JSON
                try:
                    # Убираем экранированные символы
                    fixed_json = json_str.replace('\\"', '"')  # Убираем экранированные кавычки
                    fixed_json = fixed_json.replace('\\n', '\n')  # Убираем экранированные переносы строк
                    fixed_json = fixed_json.replace('\\\\', '\\')  # Убираем двойные экранирования
                    
                    # Пробуем снова
                    result = json.loads(fixed_json)
                    logger.info(f"✅ [PARSE STEP {step}] Fixed and parsed JSON successfully")
                    return result
                    
                except json.JSONDecodeError as e2:
                    logger.error(f"❌ [PARSE STEP {step}] Failed to fix JSON: {str(e2)}")
                    
                    # Последняя попытка - используем обычную генерацию для шага 7
                    if step == 7:
                        logger.warning(f"🔄 [PARSE STEP 7] Переключение на обычную генерацию")
                        return self._fallback_code_generation(context)
                    
                    # Для других шагов возвращаем ошибку
                    raise e
                
        except Exception as e:
            logger.error(f"❌ Parse error step {step}: Ошибка обработки ответа AI: {str(e)}")
            
            # Для шага 7 используем fallback
            if step == 7:
                logger.warning(f"🔄 [PARSE STEP 7] Критическая ошибка, используем fallback генерацию")
                return self._fallback_code_generation(context)
            
            # Возвращаем ошибку в структурированном виде
            return {
                "error": True,
                "step": step,
                "message": f"Ошибка парсинга ответа: {str(e)}",
                "raw_response": str(ai_response)[:1000]  # Первые 1000 символов для отладки
            }

    def _fallback_code_generation(self, context: Dict) -> Dict:
        """Fallback генерация кода через обычный сервис"""
        try:
            logger.info("🔄 [FALLBACK] Используем обычную генерацию кода")
            
            # Формируем данные для обычной генерации
            request_data = {
                'prompt': context.get('user_prompt', 'Создай современный сайт'),
                'style': context.get('style', 'modern')
            }
            
            # Используем обычный промпт
            full_prompt = self.ai_service.build_ai_prompt(
                request_data['prompt'], 
                request_data['style']
            )
            
            # Вызываем AI
            api_response = self.ai_service.call_deepseek_api(full_prompt)
            
            # Парсим ответ через обычный сервис
            code_data = self.ai_service.parse_ai_response(api_response)
            
            return code_data
            
        except Exception as e:
            logger.error(f"❌ [FALLBACK] Ошибка fallback генерации: {str(e)}")
            # Возвращаем минимальный HTML
            return {
                "html": "<!DOCTYPE html><html><head><title>Сайт</title></head><body><h1>Добро пожаловать!</h1></body></html>",
                "css": "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }",
                "js": "console.log('Сайт загружен');"
            }

    def _fallback_generation(self, request_data: Dict) -> Dict[str, Any]:
        """Резервная генерация при ошибке премиум процесса"""
        logger.info("🔄 [FALLBACK] Переключение на стандартную генерацию")
        return self.ai_service.generate_portfolio(request_data)

    def _get_enhancement_summary(self, steps: Dict) -> List[str]:
        """Сводка улучшений премиум генерации"""
        enhancements = []
        
        if steps.get(1, {}).get('success'):
            enhancements.append("✅ Профессиональный бизнес-анализ")
        if steps.get(3, {}).get('success'):
            enhancements.append("🎨 Уникальная дизайн-концепция")
        if steps.get(4, {}).get('success'):
            enhancements.append("✍️ Продающий копирайтинг")
        if steps.get(5, {}).get('success'):
            enhancements.append("🖼️ Автоматические изображения")
        if steps.get(6, {}).get('success'):
            enhancements.append("⚡ Современная интерактивность")
            
        return enhancements

    def _detect_target_audience(self, prompt: str) -> str:
        """Определение целевой аудитории из промпта"""
        text = prompt.lower()
        
        if any(word in text for word in ['b2b', 'бизнес', 'корпоративн', 'компани']):
            return 'B2B клиенты и партнеры'
        elif any(word in text for word in ['молод', 'студент', 'школьник']):
            return 'Молодежь 18-25 лет'
        elif any(word in text for word in ['семь', 'родител', 'дети']):
            return 'Семьи с детьми'
        elif any(word in text for word in ['премиум', 'элитн', 'vip', 'люкс']):
            return 'Премиум сегмент'
        else:
            return 'Широкая аудитория'

    def _detect_primary_goals(self, prompt: str) -> List[str]:
        """Определение основных целей из промпта"""
        text = prompt.lower()
        goals = []
        
        if any(word in text for word in ['продаж', 'заказ', 'купить', 'покупк']):
            goals.append('Увеличение продаж')
        if any(word in text for word in ['заявк', 'обращени', 'звонок', 'контакт']):
            goals.append('Генерация лидов')
        if any(word in text for word in ['брен', 'узнаваем', 'имидж']):
            goals.append('Повышение узнаваемости бренда')
        if any(word in text for word in ['информаци', 'услуг', 'о нас']):
            goals.append('Информирование о услугах')
        if any(word in text for word in ['доверие', 'репутаци', 'отзыв']):
            goals.append('Построение доверия')
            
        return goals if goals else ['Привлечение клиентов']

    def _extract_usp(self, prompt: str) -> List[str]:
        """Извлечение уникальных преимуществ"""
        text = prompt.lower()
        usp = []
        
        if any(word in text for word in ['быстр', 'скорост', 'оперативн']):
            usp.append('Высокая скорость обслуживания')
        if any(word in text for word in ['качеств', 'профессионал', 'экспер']):
            usp.append('Профессиональное качество')
        if any(word in text for word in ['индивидуальн', 'персональн', 'под заказ']):
            usp.append('Индивидуальный подход')
        if any(word in text for word in ['опыт', 'лет', 'года']):
            usp.append('Многолетний опыт')
        if any(word in text for word in ['гаранти', 'надежн']):
            usp.append('Гарантия качества')
            
        return usp if usp else ['Высокое качество услуг']

    # Совместимость со старым интерфейсом
    def generate_website(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Точка входа - автоматически использует премиум генерацию"""
        return self.generate_website_premium(request_data)


# Обновляем основной класс для обратной совместимости
SmartAIGenerator = PremiumSmartAIGenerator 