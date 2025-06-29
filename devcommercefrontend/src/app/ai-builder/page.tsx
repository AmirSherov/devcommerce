'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { aiAPI } from '../../api/ai/api';
import './style.scss';

interface FormData {
  title: string;
  description: string;
  prompt: string;
  businessInfo: {
    industry: string;
    target_audience: string;
    goals: string[];
    competitors: string[];
  };
  design: {
    style: string;
    colorScheme: string;
    typography: string;
    mood: string;
  };
  content: {
    mainSections: string[];
    keyMessages: string[];
    callToActions: string[];
  };
  technical: {
    features: string[];
    animations: boolean;
    responsive: boolean;
    accessibility: boolean;
  };
}

interface UserLimits {
  is_premium: boolean;
  daily_limit: number;
  used_today: number;
  remaining_today: number;
  can_generate: boolean;
  limit_message: string;
}

const STEPS = [
  { id: 1, title: 'Бизнес-анализ', description: 'Анализ целей и аудитории' },
  { id: 2, title: 'Архитектура', description: 'Структура и UX сайта' },
  { id: 3, title: 'Дизайн', description: 'Визуальная концепция' },
  { id: 4, title: 'Контент', description: 'Стратегия контента' },
  { id: 5, title: 'Медиа', description: 'Изображения и видео' },
  { id: 6, title: 'Интерактив', description: 'Анимации и эффекты' },
  { id: 7, title: 'Оптимизация', description: 'Финальные улучшения' }
];

const DESIGN_STYLES = [
  { value: 'minimal', label: '✨ Минимализм', description: 'Чистый, современный дизайн с акцентом на контент' },
  { value: 'brutalism', label: '🏗️ Брутализм', description: 'Смелый, нестандартный дизайн с сильным характером' },
  { value: 'glassmorphism', label: '🌟 Гласморфизм', description: 'Эффект матового стекла и размытия' },
  { value: 'neumorphism', label: '💎 Неоморфизм', description: 'Мягкие тени и объемные элементы' },
  { value: 'retro', label: '📺 Ретро', description: 'Винтажная эстетика и ностальгия' },
  { value: 'cyberpunk', label: '🌆 Киберпанк', description: 'Футуристический стиль с неоновыми акцентами' }
];

const INDUSTRIES = [
  { value: 'tech', label: '💻 Технологии', description: 'IT, SaaS, стартапы' },
  { value: 'creative', label: '🎨 Креатив', description: 'Дизайн, искусство, медиа' },
  { value: 'business', label: '💼 Бизнес', description: 'Консалтинг, финансы, B2B' },
  { value: 'ecommerce', label: '🛍️ E-commerce', description: 'Онлайн-магазины, маркетплейсы' },
  { value: 'education', label: '📚 Образование', description: 'Курсы, школы, тренинги' },
  { value: 'entertainment', label: '🎮 Развлечения', description: 'Игры, медиа, контент' }
];

export default function AIBuilderPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [error, setError] = useState('');
  const [userLimits, setUserLimits] = useState<UserLimits | null>(null);

  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    prompt: '',
    businessInfo: {
      industry: 'tech',
      target_audience: '',
      goals: [],
      competitors: []
    },
    design: {
      style: 'minimal',
      colorScheme: 'monochrome',
      typography: 'modern',
      mood: 'professional'
    },
    content: {
      mainSections: [],
      keyMessages: [],
      callToActions: []
    },
    technical: {
      features: [],
      animations: true,
      responsive: true,
      accessibility: true
    }
  });

  useEffect(() => {
    loadUserLimits();
  }, []);

  const loadUserLimits = async () => {
    try {
      const response = await aiAPI.getUserLimits();
      if (response.success) {
        setUserLimits(response.data);
      }
    } catch (error) {
      console.error('Error loading user limits:', error);
    }
  };

  const handleInputChange = (section: keyof FormData, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: typeof prev[section] === 'object'
        ? { ...prev[section], [field]: value }
        : value
    }));
    setError('');
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        if (!formData.title.trim() || !formData.description.trim() || !formData.prompt.trim()) {
          setError('Заполните все обязательные поля');
          return false;
        }
        break;
      case 2:
        if (!formData.businessInfo.target_audience || formData.businessInfo.goals.length === 0) {
          setError('Укажите целевую аудиторию и цели');
          return false;
        }
        break;
      case 3:
        if (!formData.design.style || !formData.design.mood) {
          setError('Выберите стиль и настроение дизайна');
          return false;
        }
        break;
      case 4:
        if (formData.content.mainSections.length === 0) {
          setError('Добавьте хотя бы один основной раздел');
          return false;
        }
        break;
    }
    return true;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, STEPS.length));
      setError('');
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
    setError('');
  };

  const handleGenerate = async () => {
    if (!validateStep(currentStep)) return;

    if (!userLimits?.can_generate) {
      setError(userLimits?.limit_message || 'Недостаточно лимитов для генерации');
      return;
    }

    setIsGenerating(true);
    setError('');

    try {
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += 1;
        if (progress <= 100) {
          setGenerationProgress(progress);
        }
      }, 500);

      const result = await aiAPI.premiumGenerate({
        title: formData.title,
        description: formData.description,
        prompt: formData.prompt,
        business_info: formData.businessInfo,
        design_preferences: formData.design,
        content_strategy: formData.content,
        technical_requirements: formData.technical
      });

      clearInterval(progressInterval);

      if (result.success) {
        router.push(`/portfolio/preview/${result.data.id}`);
      } else {
        setError('Ошибка при генерации сайта');
      }
    } catch (error) {
      setError('Произошла ошибка. Попробуйте позже.');
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
    }
  };

  const renderBusinessStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Бизнес-анализ</h2>
        <p>Расскажите о вашем бизнесе и целях</p>
      </div>

      <div className="ai-form-group">
        <label>Название проекта <span className="required">*</span></label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => handleInputChange('title', '', e.target.value)}
          placeholder="Например: Creative Studio Portfolio"
        />
      </div>

      <div className="ai-form-group">
        <label>Описание проекта <span className="required">*</span></label>
        <textarea
          value={formData.description}
          onChange={(e) => handleInputChange('description', '', e.target.value)}
          placeholder="Опишите ваш проект, его миссию и основные цели"
        />
      </div>

      <div className="ai-form-group">
        <label>AI Промпт <span className="required">*</span></label>
        <textarea
          value={formData.prompt}
          onChange={(e) => handleInputChange('prompt', '', e.target.value)}
          placeholder="Опишите подробно, какой сайт вы хотите получить. Например: Создай современный сайт для фитнес-центра с акцентом на персональные тренировки и групповые занятия. Нужны яркие фотографии, анимации при скролле и форма записи на пробное занятие."
          rows={4}
        />
        <small className="ai-form-hint">Это описание будет использовано AI для генерации вашего сайта. Чем подробнее вы опишете свои пожелания, тем лучше будет результат.</small>
      </div>

      <div className="ai-form-group">
        <label>Индустрия</label>
        <div className="ai-options-grid">
          {INDUSTRIES.map(industry => (
            <div
              key={industry.value}
              className={`ai-option ${formData.businessInfo.industry === industry.value ? 'selected' : ''}`}
              onClick={() => handleInputChange('businessInfo', 'industry', industry.value)}
            >
              <div className="ai-option-header">
                <span className="ai-option-icon">{industry.label.split(' ')[0]}</span>
                <span className="ai-option-title">{industry.label.split(' ').slice(1).join(' ')}</span>
              </div>
              <p className="ai-option-description">{industry.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderArchitectureStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Архитектура</h2>
        <p>Определите структуру и UX сайта</p>
      </div>

      <div className="ai-form-group">
        <label>Целевая аудитория <span className="required">*</span></label>
        <textarea
          value={formData.businessInfo.target_audience}
          onChange={(e) => handleInputChange('businessInfo', 'target_audience', e.target.value)}
          placeholder="Опишите вашу целевую аудиторию: возраст, интересы, потребности..."
        />
      </div>

      <div className="ai-form-group">
        <label>Цели проекта <span className="required">*</span></label>
        <div className="ai-tags-input">
          <input
            type="text"
            placeholder="Добавьте цель и нажмите Enter"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value) {
                  handleInputChange('businessInfo', 'goals', [...formData.businessInfo.goals, value]);
                  input.value = '';
                }
              }
            }}
          />
          <div className="ai-tags">
            {formData.businessInfo.goals.map((goal, index) => (
              <span key={index} className="ai-tag">
                {goal}
                <button
                  onClick={() => {
                    const newGoals = formData.businessInfo.goals.filter((_, i) => i !== index);
                    handleInputChange('businessInfo', 'goals', newGoals);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="ai-form-group">
        <label>Конкуренты</label>
        <div className="ai-tags-input">
          <input
            type="text"
            placeholder="Добавьте конкурента и нажмите Enter"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value) {
                  handleInputChange('businessInfo', 'competitors', [...formData.businessInfo.competitors, value]);
                  input.value = '';
                }
              }
            }}
          />
          <div className="ai-tags">
            {formData.businessInfo.competitors.map((competitor, index) => (
              <span key={index} className="ai-tag">
                {competitor}
                <button
                  onClick={() => {
                    const newCompetitors = formData.businessInfo.competitors.filter((_, i) => i !== index);
                    handleInputChange('businessInfo', 'competitors', newCompetitors);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderDesignStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Дизайн</h2>
        <p>Выберите визуальный стиль сайта</p>
      </div>

      <div className="ai-form-group">
        <label>Стиль дизайна</label>
        <div className="ai-options-grid">
          {DESIGN_STYLES.map(style => (
            <div
              key={style.value}
              className={`ai-option ${formData.design.style === style.value ? 'selected' : ''}`}
              onClick={() => handleInputChange('design', 'style', style.value)}
            >
              <div className="ai-option-header">
                <span className="ai-option-icon">{style.label.split(' ')[0]}</span>
                <span className="ai-option-title">{style.label.split(' ').slice(1).join(' ')}</span>
              </div>
              <p className="ai-option-description">{style.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderContentStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Контент</h2>
        <p>Определите структуру контента сайта</p>
      </div>

      <div className="ai-form-group">
        <label>Основные разделы <span className="required">*</span></label>
        <div className="ai-tags-input">
          <input
            type="text"
            placeholder="Добавьте раздел и нажмите Enter"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value) {
                  handleInputChange('content', 'mainSections', [...formData.content.mainSections, value]);
                  input.value = '';
                }
              }
            }}
          />
          <div className="ai-tags">
            {formData.content.mainSections.map((section, index) => (
              <span key={index} className="ai-tag">
                {section}
                <button
                  onClick={() => {
                    const newSections = formData.content.mainSections.filter((_, i) => i !== index);
                    handleInputChange('content', 'mainSections', newSections);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="ai-form-group">
        <label>Ключевые сообщения</label>
        <div className="ai-tags-input">
          <input
            type="text"
            placeholder="Добавьте сообщение и нажмите Enter"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value) {
                  handleInputChange('content', 'keyMessages', [...formData.content.keyMessages, value]);
                  input.value = '';
                }
              }
            }}
          />
          <div className="ai-tags">
            {formData.content.keyMessages.map((message, index) => (
              <span key={index} className="ai-tag">
                {message}
                <button
                  onClick={() => {
                    const newMessages = formData.content.keyMessages.filter((_, i) => i !== index);
                    handleInputChange('content', 'keyMessages', newMessages);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="ai-form-group">
        <label>Призывы к действию</label>
        <div className="ai-tags-input">
          <input
            type="text"
            placeholder="Добавьте CTA и нажмите Enter"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value) {
                  handleInputChange('content', 'callToActions', [...formData.content.callToActions, value]);
                  input.value = '';
                }
              }
            }}
          />
          <div className="ai-tags">
            {formData.content.callToActions.map((cta, index) => (
              <span key={index} className="ai-tag">
                {cta}
                <button
                  onClick={() => {
                    const newCTAs = formData.content.callToActions.filter((_, i) => i !== index);
                    handleInputChange('content', 'callToActions', newCTAs);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderMediaStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Медиа</h2>
        <p>Настройте визуальный контент</p>
      </div>

      <div className="ai-form-group">
        <label>Типография</label>
        <select
          value={formData.design.typography}
          onChange={(e) => handleInputChange('design', 'typography', e.target.value)}
        >
          <option value="modern">Современная</option>
          <option value="classic">Классическая</option>
          <option value="minimal">Минималистичная</option>
          <option value="creative">Креативная</option>
          <option value="tech">Техническая</option>
        </select>
      </div>

      <div className="ai-form-group">
        <label>Настроение</label>
        <select
          value={formData.design.mood}
          onChange={(e) => handleInputChange('design', 'mood', e.target.value)}
        >
          <option value="professional">Профессиональное</option>
          <option value="friendly">Дружелюбное</option>
          <option value="luxury">Премиальное</option>
          <option value="playful">Игривое</option>
          <option value="serious">Серьезное</option>
          <option value="innovative">Инновационное</option>
        </select>
      </div>
    </div>
  );

  const renderInteractiveStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Интерактивность</h2>
        <p>Настройте анимации и эффекты</p>
      </div>

      <div className="ai-form-group">
        <label>Технические требования</label>
        <div className="ai-checkbox-group">
          <label className="ai-checkbox">
            <input
              type="checkbox"
              checked={formData.technical.animations}
              onChange={(e) => handleInputChange('technical', 'animations', e.target.checked)}
            />
            <span>Анимации и эффекты</span>
          </label>

          <label className="ai-checkbox">
            <input
              type="checkbox"
              checked={formData.technical.responsive}
              onChange={(e) => handleInputChange('technical', 'responsive', e.target.checked)}
            />
            <span>Адаптивный дизайн</span>
          </label>

          <label className="ai-checkbox">
            <input
              type="checkbox"
              checked={formData.technical.accessibility}
              onChange={(e) => handleInputChange('technical', 'accessibility', e.target.checked)}
            />
            <span>Доступность (a11y)</span>
          </label>
        </div>
      </div>

      <div className="ai-form-group">
        <label>Особые функции</label>
        <div className="ai-tags-input">
          <input
            type="text"
            placeholder="Добавьте функцию и нажмите Enter"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const input = e.target as HTMLInputElement;
                const value = input.value.trim();
                if (value) {
                  handleInputChange('technical', 'features', [...formData.technical.features, value]);
                  input.value = '';
                }
              }
            }}
          />
          <div className="ai-tags">
            {formData.technical.features.map((feature, index) => (
              <span key={index} className="ai-tag">
                {feature}
                <button
                  onClick={() => {
                    const newFeatures = formData.technical.features.filter((_, i) => i !== index);
                    handleInputChange('technical', 'features', newFeatures);
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderOptimizationStep = () => (
    <div className="ai-step">
      <div className="ai-step-header">
        <h2>Оптимизация</h2>
        <p>Проверьте все настройки перед генерацией</p>
      </div>

      <div className="ai-summary">
        <div className="ai-summary-section">
          <h3>Бизнес</h3>
          <div className="ai-summary-item">
            <span>Название:</span>
            <span>{formData.title}</span>
          </div>
          <div className="ai-summary-item">
            <span>Индустрия:</span>
            <span>{formData.businessInfo.industry}</span>
          </div>
          <div className="ai-summary-item">
            <span>Цели:</span>
            <span>{formData.businessInfo.goals.length} определено</span>
          </div>
        </div>

        <div className="ai-summary-section">
          <h3>Дизайн</h3>
          <div className="ai-summary-item">
            <span>Стиль:</span>
            <span>{formData.design.style}</span>
          </div>
          <div className="ai-summary-item">
            <span>Типография:</span>
            <span>{formData.design.typography}</span>
          </div>
          <div className="ai-summary-item">
            <span>Настроение:</span>
            <span>{formData.design.mood}</span>
          </div>
        </div>

        <div className="ai-summary-section">
          <h3>Контент</h3>
          <div className="ai-summary-item">
            <span>Разделы:</span>
            <span>{formData.content.mainSections.length} определено</span>
          </div>
          <div className="ai-summary-item">
            <span>Сообщения:</span>
            <span>{formData.content.keyMessages.length} определено</span>
          </div>
          <div className="ai-summary-item">
            <span>CTA:</span>
            <span>{formData.content.callToActions.length} определено</span>
          </div>
        </div>

        <div className="ai-summary-section">
          <h3>Технические</h3>
          <div className="ai-summary-item">
            <span>Анимации:</span>
            <span>{formData.technical.animations ? 'Да' : 'Нет'}</span>
          </div>
          <div className="ai-summary-item">
            <span>Адаптивность:</span>
            <span>{formData.technical.responsive ? 'Да' : 'Нет'}</span>
          </div>
          <div className="ai-summary-item">
            <span>Доступность:</span>
            <span>{formData.technical.accessibility ? 'Да' : 'Нет'}</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderBusinessStep();
      case 2:
        return renderArchitectureStep();
      case 3:
        return renderDesignStep();
      case 4:
        return renderContentStep();
      case 5:
        return renderMediaStep();
      case 6:
        return renderInteractiveStep();
      case 7:
        return renderOptimizationStep();
      default:
        return <div>Step {currentStep}</div>;
    }
  };

  if (isGenerating) {
    return (
      <div className="ai-builder-page">
        <div className="ai-builder-container">
          <div className="ai-generating">
            <div className="ai-generating-icon">⚡</div>
            <div className="ai-generating-text">
              {STEPS[Math.floor((generationProgress / 100) * (STEPS.length - 1))].title}
            </div>
            <div className="ai-generating-subtext">
              {STEPS[Math.floor((generationProgress / 100) * (STEPS.length - 1))].description}
            </div>
            <div className="ai-progress-bar">
              <div className="ai-progress-fill" style={{ width: `${generationProgress}%` }} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-builder-page">
      <div className="ai-builder-container">
        <div className="ai-builder-header">
          <div className="ai-builder-title">
            <h1>AI Website Builder</h1>
            <p>Создайте уникальный сайт с помощью искусственного интеллекта</p>
          </div>

          {userLimits && (
            <div className={`ai-limits ${userLimits.can_generate ? 'available' : 'exhausted'}`}>
              <div className="ai-limits-text">
                <span className="ai-limits-count">{userLimits.remaining_today}</span>
                <span className="ai-limits-label">генераций осталось</span>
                {userLimits.is_premium && (
                  <span className="ai-limits-premium">PREMIUM</span>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="ai-progress">
          <div className="ai-progress-steps">
            {STEPS.map((step, index) => (
              <div
                key={step.id}
                className={`ai-progress-step ${currentStep >= step.id ? 'active' : ''} ${currentStep === step.id ? 'current' : ''}`}
              >
                <div className="ai-progress-step-number">{step.id}</div>
                <div className="ai-progress-step-label">{step.title}</div>
              </div>
            ))}
          </div>
        </div>

        {error && <div className="ai-error">{error}</div>}

        {renderCurrentStep()}

        <div className="ai-buttons" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem' }}>
          {currentStep > 1 && (
            <button className="ai-button secondary" onClick={prevStep}>
              Назад
            </button>
          )}
          {currentStep < STEPS.length ? (
            <button className="ai-button primary" onClick={nextStep}>
              Далее
            </button>
          ) : (
            <button
              className="ai-button primary"
              onClick={handleGenerate}
              disabled={!userLimits?.can_generate}
            >
              Создать сайт
            </button>
          )}
        </div>
      </div>
    </div>
  );
} 