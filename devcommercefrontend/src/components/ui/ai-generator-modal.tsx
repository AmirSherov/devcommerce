'use client';

import { useState, useEffect } from 'react';
import { aiAPI } from '../../api/ai/api';

interface AIGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (portfolio: any, generationTime?: number) => void;
  isPremium: boolean;
}

interface AIFormData {
  title: string;
  description: string;
  prompt: string;
  style: string;
  tags: string[];
}

const STYLE_OPTIONS = [
  { value: 'modern', label: 'Современный', description: 'Чистые линии, градиенты, анимации' },
  { value: 'minimal', label: 'Минимализм', description: 'Много белого пространства, простота' },
  { value: 'creative', label: 'Креативный', description: 'Яркий дизайн, необычные элементы' },
  { value: 'business', label: 'Бизнес', description: 'Строгий стиль, профессиональные цвета' },
  { value: 'dark', label: 'Темная тема', description: 'Темный фон, контрастные элементы' },
  { value: 'colorful', label: 'Яркий', description: 'Красочный дизайн, насыщенные цвета' },
];

const PROMPT_EXAMPLES = [
  'Создай лендинг для IT-стартапа с темной темой и неоновыми акцентами',
  'Сделай портфолио фотографа с галереей и контактной формой',
  'Лендинг для ресторана с меню и бронированием столиков',
  'Корпоративный сайт для юридической компании',
  'Креативное портфолио дизайнера с анимациями',
  'Лендинг для фитнес-центра с расписанием тренировок',
  'Сайт для кофейни с уютным дизайном и картой',
  'Портфолио разработчика с проектами и навыками'
];

export default function AIGeneratorModal({ isOpen, onClose, onSuccess, isPremium }: AIGeneratorModalProps) {
  const [formData, setFormData] = useState<AIFormData>({
    title: '',
    description: '',
    prompt: '',
    style: 'modern',
    tags: []
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(1);
  const [showExamples, setShowExamples] = useState(false);
  const [userLimits, setUserLimits] = useState(null);

  // Загружаем лимиты пользователя при открытии
  useEffect(() => {
    if (isOpen && isPremium) {
      loadUserLimits();
    }
  }, [isOpen, isPremium]);

  const loadUserLimits = async () => {
    try {
      const limits = await aiAPI.getUserLimits();
      setUserLimits(limits);
    } catch (error) {
      console.error('Error loading user limits:', error);
    }
  };

  const handleInputChange = (field: keyof AIFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
  };

  const handleTagsChange = (tagsString: string) => {
    const tags = tagsString
      .split(',')
      .map(tag => tag.trim().toLowerCase())
      .filter(tag => tag.length > 0);
    
    handleInputChange('tags', tags.slice(0, 10)); // Максимум 10 тегов
  };

  const handleExampleClick = (example: string) => {
    setFormData(prev => ({
      ...prev,
      prompt: example
    }));
    setShowExamples(false);
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Введите название проекта');
      return false;
    }
    if (formData.title.trim().length < 3) {
      setError('Название должно содержать минимум 3 символа');
      return false;
    }
    if (!formData.prompt.trim()) {
      setError('Введите промпт для AI');
      return false;
    }
    if (formData.prompt.trim().length < 10) {
      setError('Промпт должен содержать минимум 10 символов');
      return false;
    }
    return true;
  };

  const handleGenerate = async () => {
    if (!validateForm()) return;

    setIsGenerating(true);
    setError('');
    setCurrentStep(2);

    try {
      const result = await aiAPI.generatePortfolio({
        title: formData.title.trim(),
        description: formData.description.trim(),
        prompt: formData.prompt.trim(),
        style: formData.style,
        tags: formData.tags
      });

      if (result.success) {
        setCurrentStep(3);
        setTimeout(() => {
          onSuccess(result.portfolio, result.response_time);
          handleClose();
        }, 2000);
      } else {
        setError(result.error || 'Ошибка генерации');
        setCurrentStep(1);
      }
    } catch (error: any) {
      setError(error.message || 'Произошла ошибка при генерации');
      setCurrentStep(1);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      prompt: '',
      style: 'modern',
      tags: []
    });
    setError('');
    setCurrentStep(1);
    setIsGenerating(false);
    setShowExamples(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div className="bg-black border-2 border-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-black text-lg font-bold">AI</span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">AI Генератор</h2>
              <p className="text-gray-400 text-xs">Создание сайта с помощью ИИ</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={isGenerating}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-4 py-3 border-b border-white">
          <div className="flex items-center space-x-3">
            <div className={`flex items-center space-x-1 ${currentStep >= 1 ? 'text-white' : 'text-gray-500'}`}>
              <div className={`w-6 h-6 rounded-full border flex items-center justify-center text-xs ${
                currentStep >= 1 ? 'border-white bg-white text-black' : 'border-gray-500'
              }`}>
                {currentStep > 1 ? '✓' : '1'}
              </div>
              <span className="text-xs font-medium">Настройка</span>
            </div>
            <div className={`flex-1 h-px ${currentStep >= 2 ? 'bg-white' : 'bg-gray-600'}`}></div>
            <div className={`flex items-center space-x-1 ${currentStep >= 2 ? 'text-white' : 'text-gray-500'}`}>
              <div className={`w-6 h-6 rounded-full border flex items-center justify-center text-xs ${
                currentStep >= 2 ? 'border-white bg-white text-black' : 'border-gray-500'
              }`}>
                {currentStep > 2 ? '✓' : '2'}
              </div>
              <span className="text-xs font-medium">Генерация</span>
            </div>
            <div className={`flex-1 h-px ${currentStep >= 3 ? 'bg-white' : 'bg-gray-600'}`}></div>
            <div className={`flex items-center space-x-1 ${currentStep >= 3 ? 'text-white' : 'text-gray-500'}`}>
              <div className={`w-6 h-6 rounded-full border flex items-center justify-center text-xs ${
                currentStep >= 3 ? 'border-white bg-white text-black' : 'border-gray-500'
              }`}>
                {currentStep >= 3 ? '✓' : '3'}
              </div>
              <span className="text-xs font-medium">Готово</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {currentStep === 1 && (
            <div className="space-y-6">
              {/* Лимиты пользователя */}
              {userLimits && (
                <div className="bg-gray-800 border border-gray-600 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">Осталось генераций сегодня:</span>
                    <span className="text-blue-400 font-bold">{userLimits.remaining_today}/5</span>
                  </div>
                  {userLimits.remaining_today === 0 && (
                    <p className="text-red-400 text-sm mt-2">Дневной лимит исчерпан. Сбросится завтра.</p>
                  )}
                </div>
              )}

              {/* Название проекта */}
              <div>
                <label className="block text-white font-medium mb-2">
                  Название проекта <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="Например: Лендинг для IT компании"
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none transition-colors"
                  maxLength={200}
                />
                <p className="text-gray-400 text-xs mt-1">{formData.title.length}/200</p>
              </div>

              {/* Описание */}
              <div>
                <label className="block text-white font-medium mb-2">
                  Описание (необязательно)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Краткое описание вашего проекта"
                  rows={3}
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none transition-colors resize-none"
                  maxLength={1000}
                />
                <p className="text-gray-400 text-xs mt-1">{formData.description.length}/1000</p>
              </div>

              {/* AI Промпт */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-white font-medium">
                    AI Промпт <span className="text-red-400">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowExamples(!showExamples)}
                    className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
                  >
                    {showExamples ? 'Скрыть примеры' : 'Показать примеры'}
                  </button>
                </div>
                
                {showExamples && (
                  <div className="mb-4 bg-gray-800 border border-gray-600 rounded-lg p-4">
                    <p className="text-gray-300 text-sm mb-3">Нажмите на пример чтобы использовать:</p>
                    <div className="space-y-2">
                      {PROMPT_EXAMPLES.map((example, index) => (
                        <button
                          key={index}
                          onClick={() => handleExampleClick(example)}
                          className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 text-sm transition-colors"
                        >
                          {example}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <textarea
                  value={formData.prompt}
                  onChange={(e) => handleInputChange('prompt', e.target.value)}
                  placeholder="Опишите какой сайт вы хотите создать: тематику, стиль, функции..."
                  rows={4}
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none transition-colors resize-none"
                  maxLength={500}
                />
                <p className="text-gray-400 text-xs mt-1">{formData.prompt.length}/500</p>
              </div>

              {/* Стиль дизайна */}
              <div>
                <label className="block text-white font-medium mb-3">Стиль дизайна</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {STYLE_OPTIONS.map((style) => (
                    <label
                      key={style.value}
                      className={`cursor-pointer p-4 border-2 rounded-lg transition-all ${
                        formData.style === style.value
                          ? 'border-blue-400 bg-blue-400 bg-opacity-10'
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <input
                        type="radio"
                        name="style"
                        value={style.value}
                        checked={formData.style === style.value}
                        onChange={(e) => handleInputChange('style', e.target.value)}
                        className="sr-only"
                      />
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          formData.style === style.value ? 'border-blue-400 bg-blue-400' : 'border-gray-500'
                        }`}>
                          {formData.style === style.value && (
                            <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
                          )}
                        </div>
                        <div>
                          <p className="text-white font-medium">{style.label}</p>
                          <p className="text-gray-400 text-sm">{style.description}</p>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Теги */}
              <div>
                <label className="block text-white font-medium mb-2">
                  Теги (через запятую)
                </label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => handleTagsChange(e.target.value)}
                  placeholder="landing, business, modern"
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none transition-colors"
                />
                <p className="text-gray-400 text-xs mt-1">Максимум 10 тегов</p>
              </div>

              {/* Ошибка */}
              {error && (
                <div className="bg-red-900 bg-opacity-50 border border-red-600 rounded-lg p-4">
                  <p className="text-red-400">{error}</p>
                </div>
              )}
            </div>
          )}

          {currentStep === 2 && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto mb-4 bg-white rounded-full flex items-center justify-center animate-pulse">
                <span className="text-black text-xl font-bold">AI</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-3">Генерируем сайт...</h3>
              <div className="space-y-1 text-gray-400 text-sm">
                <p>• Анализируем промпт</p>
                <p>• Создаём структуру</p>
                <p>• Собираем код</p>
              </div>
              <div className="mt-4">
                <div className="w-full bg-gray-800 border border-white rounded-full h-1">
                  <div className="bg-white h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                </div>
              </div>
              <p className="text-gray-500 text-xs mt-3">Обычно занимает 10-30 секунд</p>
            </div>
          )}

          {currentStep === 3 && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto mb-4 bg-white rounded-full flex items-center justify-center">
                <span className="text-black text-lg font-bold">✓</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Сайт создан!</h3>
              <p className="text-gray-400 text-sm">Перенаправляем...</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {currentStep === 1 && (
          <div className="flex items-center justify-between p-4 border-t border-white">
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-gray-800 border border-white hover:bg-gray-700 text-white rounded-lg transition-colors"
              disabled={isGenerating}
            >
              Отмена
            </button>
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !isPremium || (userLimits && userLimits.remaining_today === 0)}
              className="px-4 py-2 bg-white hover:bg-gray-200 text-black rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isGenerating ? 'Генерируем...' : 'Создать сайт'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 