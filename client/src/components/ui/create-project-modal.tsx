'use client';

import { useState } from 'react';
import Modal from './modal';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (projectData: ProjectFormData) => Promise<void>;
  isLoading?: boolean;
  maxProjects?: number;
  currentProjectsCount?: number;
}

export interface ProjectFormData {
  title: string;
  description: string;
  is_public: boolean;
  tags: string[];
}

export default function CreateProjectModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  maxProjects = 5,
  currentProjectsCount = 0,
}: CreateProjectModalProps) {
  const [formData, setFormData] = useState<ProjectFormData>({
    title: '',
    description: '',
    is_public: true,
    tags: ['html', 'css', 'javascript'],
  });

  const [errors, setErrors] = useState<Partial<ProjectFormData>>({});
  const [customTag, setCustomTag] = useState('');

  // Предустановленные теги
  const availableTags = [
    'html', 'css', 'javascript', 'react', 'vue', 'angular', 
    'typescript', 'tailwind', 'bootstrap', 'sass', 'nodejs',
    'responsive', 'animation', 'portfolio', 'landing'
  ];

  // Валидация формы
  const validateForm = (): boolean => {
    const newErrors: Partial<ProjectFormData> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Название проекта обязательно';
    } else if (formData.title.length < 3) {
      newErrors.title = 'Название должно содержать минимум 3 символа';
    } else if (formData.title.length > 100) {
      newErrors.title = 'Название не должно превышать 100 символов';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Описание проекта обязательно';
    } else if (formData.description.length < 10) {
      newErrors.description = 'Описание должно содержать минимум 10 символов';
    } else if (formData.description.length > 500) {
      newErrors.description = 'Описание не должно превышать 500 символов';
    }

    if (formData.tags.length === 0) {
      newErrors.tags = 'Выберите хотя бы один тег';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Обработка отправки формы
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      await onSubmit(formData);
      // Сброс формы после успешного создания
      setFormData({
        title: '',
        description: '',
        is_public: true,
        tags: ['html', 'css', 'javascript'],
      });
      setErrors({});
      setCustomTag('');
    } catch (error) {
      // Ошибка обрабатывается в родительском компоненте
    }
  };

  // Обработка изменения полей
  const handleInputChange = (field: keyof ProjectFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Очищаем ошибку для этого поля
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // Добавление/удаление тегов
  const toggleTag = (tag: string) => {
    const newTags = formData.tags.includes(tag)
      ? formData.tags.filter(t => t !== tag)
      : [...formData.tags, tag];
    
    handleInputChange('tags', newTags);
  };

  // Добавление кастомного тега
  const addCustomTag = () => {
    const tag = customTag.trim().toLowerCase();
    if (tag && !formData.tags.includes(tag) && !availableTags.includes(tag)) {
      handleInputChange('tags', [...formData.tags, tag]);
      setCustomTag('');
    }
  };

  // Закрытие модального окна
  const handleClose = () => {
    if (isLoading) return;
    onClose();
    // Сброс формы при закрытии
    setTimeout(() => {
      setFormData({
        title: '',
        description: '',
        is_public: true,
        tags: ['html', 'css', 'javascript'],
      });
      setErrors({});
      setCustomTag('');
    }, 300);
  };

  const isAtLimit = currentProjectsCount >= maxProjects;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Создать новый проект"
      size="lg"
      closeOnOverlayClick={!isLoading}
      closeOnEscape={!isLoading}
    >
      <form onSubmit={handleSubmit} className="p-6">
        {/* Предупреждение о лимите */}
        {isAtLimit && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="text-red-400 text-sm font-medium">
                Достигнут лимит проектов ({currentProjectsCount}/{maxProjects})
              </span>
            </div>
          </div>
        )}

        {/* Название проекта */}
        <div className="mb-6">
          <label htmlFor="title" className="block text-sm font-medium text-white mb-2">
            Название проекта *
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            disabled={isLoading || isAtLimit}
            placeholder="Мой потрясающий проект"
            className={`
              w-full px-4 py-3 bg-gray-900 border rounded-lg text-white placeholder-gray-500
              focus:outline-none focus:ring-2 transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              ${errors.title 
                ? 'border-red-500 focus:ring-red-500/50' 
                : 'border-gray-600 focus:border-gray-500 focus:ring-white/20'
              }
            `}
          />
          {errors.title && (
            <p className="mt-2 text-sm text-red-400">{errors.title}</p>
          )}
        </div>

        {/* Описание */}
        <div className="mb-6">
          <label htmlFor="description" className="block text-sm font-medium text-white mb-2">
            Описание проекта *
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            disabled={isLoading || isAtLimit}
            placeholder="Расскажите о вашем проекте, его особенностях и технологиях..."
            rows={4}
            className={`
              w-full px-4 py-3 bg-gray-900 border rounded-lg text-white placeholder-gray-500
              focus:outline-none focus:ring-2 transition-all duration-200 resize-none
              disabled:opacity-50 disabled:cursor-not-allowed
              ${errors.description 
                ? 'border-red-500 focus:ring-red-500/50' 
                : 'border-gray-600 focus:border-gray-500 focus:ring-white/20'
              }
            `}
          />
          <div className="flex justify-between mt-1">
            {errors.description ? (
              <p className="text-sm text-red-400">{errors.description}</p>
            ) : (
              <span className="text-sm text-gray-500">
                {formData.description.length}/500 символов
              </span>
            )}
          </div>
        </div>

        {/* Статус публичности */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-white mb-3">
            Статус проекта
          </label>
          <div className="space-y-3">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="visibility"
                checked={formData.is_public}
                onChange={() => handleInputChange('is_public', true)}
                disabled={isLoading || isAtLimit}
                className="sr-only"
              />
              <div className={`
                w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                ${formData.is_public 
                  ? 'border-blue-500 bg-blue-500' 
                  : 'border-gray-600'
                }
              `}>
                {formData.is_public && (
                  <div className="w-2 h-2 rounded-full bg-white"></div>
                )}
              </div>
              <div>
                <span className="text-white font-medium">Публичный</span>
                <p className="text-sm text-gray-400">Проект будет виден всем пользователям</p>
              </div>
            </label>
            
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="visibility"
                checked={!formData.is_public}
                onChange={() => handleInputChange('is_public', false)}
                disabled={isLoading || isAtLimit}
                className="sr-only"
              />
              <div className={`
                w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                ${!formData.is_public 
                  ? 'border-blue-500 bg-blue-500' 
                  : 'border-gray-600'
                }
              `}>
                {!formData.is_public && (
                  <div className="w-2 h-2 rounded-full bg-white"></div>
                )}
              </div>
              <div>
                <span className="text-white font-medium">Приватный</span>
                <p className="text-sm text-gray-400">Проект виден только вам</p>
              </div>
            </label>
          </div>
        </div>

        {/* Теги */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-white mb-3">
            Теги проекта *
          </label>
          
          {/* Предустановленные теги */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            {availableTags.map(tag => (
              <button
                key={tag}
                type="button"
                onClick={() => toggleTag(tag)}
                disabled={isLoading || isAtLimit}
                className={`
                  px-3 py-2 text-sm rounded-lg border transition-all duration-200
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${formData.tags.includes(tag)
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-gray-800 border-gray-600 text-gray-300 hover:border-gray-500 hover:bg-gray-700'
                  }
                `}
              >
                {tag}
              </button>
            ))}
          </div>

          {/* Кастомный тег */}
          <div className="flex space-x-2">
            <input
              type="text"
              value={customTag}
              onChange={(e) => setCustomTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomTag())}
              disabled={isLoading || isAtLimit}
              placeholder="Добавить свой тег"
              className="
                flex-1 px-3 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-500
                focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-gray-500
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            />
            <button
              type="button"
              onClick={addCustomTag}
              disabled={isLoading || isAtLimit || !customTag.trim()}
              className="
                px-4 py-2 bg-gray-800 border border-gray-600 text-gray-300 rounded-lg
                hover:bg-gray-700 hover:text-white hover:border-gray-500
                focus:outline-none focus:ring-2 focus:ring-white/20
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
              "
            >
              Добавить
            </button>
          </div>

          {/* Выбранные теги */}
          {formData.tags.length > 0 && (
            <div className="mt-3">
              <p className="text-sm text-gray-400 mb-2">Выбранные теги:</p>
              <div className="flex flex-wrap gap-2">
                {formData.tags.map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded-full"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => toggleTag(tag)}
                      disabled={isLoading || isAtLimit}
                      className="ml-2 hover:text-blue-200 focus:outline-none"
                    >
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {errors.tags && (
            <p className="mt-2 text-sm text-red-400">{errors.tags}</p>
          )}
        </div>

        {/* Кнопки действий */}
        <div className="flex space-x-3 justify-end">
          <button
            type="button"
            onClick={handleClose}
            disabled={isLoading}
            className="
              px-6 py-3 text-sm font-medium text-gray-300 
              bg-gray-800 border border-gray-600 rounded-lg
              hover:bg-gray-700 hover:text-white hover:border-gray-500
              focus:outline-none focus:ring-2 focus:ring-gray-500/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          >
            Отмена
          </button>
          
          <button
            type="submit"
            disabled={isLoading || isAtLimit}
            className="
              px-6 py-3 text-sm font-medium text-white rounded-lg
              bg-blue-600 hover:bg-blue-700 
              focus:outline-none focus:ring-2 focus:ring-blue-500/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200 min-w-[120px]
            "
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Создание...
              </div>
            ) : (
              'Создать проект'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
} 