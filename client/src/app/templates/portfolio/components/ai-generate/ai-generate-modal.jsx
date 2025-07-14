'use client';

import { useState, useEffect } from 'react';
import { aiAPI, getAIErrorMessage, DEFAULT_USER_DATA_PLACEHOLDER } from '../../../../../api/ai/api';
import './ai-generate-modal.scss';
import Loader from '@/components/simple-loader';
export default function AIGenerateModal({ 
  isOpen, 
  onClose, 
  template, 
  onSuccess, 
  isGeneratingAI,
  setIsGeneratingAI
}) {
  const [formData, setFormData] = useState({
    projectTitle: '',
    projectDescription: '',
    userData: ''
  });

  const [errors, setErrors] = useState({});
  const [userLimits, setUserLimits] = useState(null);
  const [loadingLimits, setLoadingLimits] = useState(true);
  // Загружаем лимиты пользователя при открытии модального окна
  useEffect(() => {
    if (isOpen) {
      loadUserLimits();
    }
  }, [isOpen]);

  const loadUserLimits = async () => {
    try {
      setLoadingLimits(true);
      const response = await aiAPI.getUserLimits();
      const limits = response.data || response;
      
      setUserLimits(limits);
    } catch (error) {
    } finally {
      setLoadingLimits(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGeneratingAI(true);
    const newErrors = {};
    if (!formData.projectTitle.trim() || formData.projectTitle.trim().length < 3) {
      newErrors.projectTitle = 'Название проекта слишком короткое (минимум 3 символа)';
    }
    if (!formData.projectDescription.trim() || formData.projectDescription.trim().length < 10) {
      newErrors.projectDescription = 'Описание проекта слишком короткое (минимум 10 символов)';
    }
    if (!formData.userData.trim()) {
      newErrors.userData = 'Введите данные пользователя';
    } else if (formData.userData.trim().length < 20) {
      newErrors.userData = 'Данные пользователя слишком короткие (минимум 20 символов)';
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      setIsGeneratingAI(false);
      return;
    }

    handleClose(); // Закрываем модалку сразу после валидации

    try {
      const result = await aiAPI.generateTemplate(template.id, {
        projectTitle: formData.projectTitle,
        projectDescription: formData.projectDescription,
        userData: formData.userData,
      });
      if (result.success) {
        onSuccess(result);
      }
    } catch (error) {
      setErrors(error.message);
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Убираем ошибку при изменении поля
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleClose = () => {
    setFormData({ projectTitle: '', projectDescription: '', userData: '' });
    setErrors({});
    setIsGeneratingAI(false); // Всегда выключаем лоадер при закрытии
    onClose();
  };

  const fillExampleData = () => {
    setFormData(prev => ({
      ...prev,
      userData: DEFAULT_USER_DATA_PLACEHOLDER
    }));
  };

  if (!isOpen) return null;
  const canUseAI = Boolean(userLimits?.can_generate);
  const isPremium = Boolean(userLimits?.is_premium);

  return (
    <div className="ai-generate-modal-overlay" onClick={handleClose}>
      <div className="ai-generate-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-content">
            <div className="header-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
              </svg>
            </div>
            <div className="header-text">
              <h2 className="modal-title">AI заполнение шаблона</h2>
              <p className="modal-subtitle">
                Персонализируем шаблон: <span className="template-name">{template?.title}</span>
              </p>
            </div>
          </div>
          <button 
            onClick={handleClose}
            disabled={isGeneratingAI}
            className="modal-close-button"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="modal-content">
          {/* Limits Info */}
          {loadingLimits ? (
            <div className="limits-loading">
              <div className="spinner"></div>
              <span>Проверяем лимиты...</span>
            </div>
          ) : userLimits && (
            <div className={`limits-info ${canUseAI ? 'success' : 'warning'}`}>
              <div className="limits-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  {isPremium ? (
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
                  ) : (
                    <circle cx="12" cy="12" r="10"></circle>
                  )}
                  {!canUseAI && <line x1="15" y1="9" x2="9" y2="15"></line>}
                </svg>
                <div className="limits-text">
                  <span className="status-badge">
                    {isPremium ? '👑 Premium' : '🔓 Базовый'}
                  </span>
                  <span className="usage-info">
                    Использовано: {userLimits.used_today} / {userLimits.daily_limit}
                  </span>
                </div>
              </div>
              <p className="limits-message">{userLimits.limit_message}</p>
            </div>
          )}

          {/* Form */}
          {canUseAI ? (
            <form onSubmit={handleSubmit} className="ai-form">
              {/* Template Preview */}
              <div className="template-preview-card">
                <div className="preview-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21,15 16,10 5,21"></polyline>
                  </svg>
                </div>
                <div className="preview-info">
                  <h4>{template?.title}</h4>
                  <p>{template?.category_display}</p>
                  <div className="ai-badge">
                    <span>🤖 AI заполнение</span>
                  </div>
                </div>
              </div>

              {/* General Error */}
              {errors.general && (
                <div className="error-message general">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                  </svg>
                  {errors.general}
                </div>
              )}

              {/* Form Fields */}
              <div className="form-fields">
                {/* Project Title */}
                <div className="field-group">
                  <label htmlFor="project-title" className="field-label">
                    Название проекта <span className="required">*</span>
                  </label>
                  <input
                    id="project-title"
                    type="text"
                    value={formData.projectTitle}
                    onChange={(e) => handleChange('projectTitle', e.target.value)}
                    placeholder="Портфолио Frontend разработчика"
                    className={`field-input ${errors.projectTitle ? 'error' : ''}`}
                    disabled={isGeneratingAI}
                    maxLength={200}
                  />
                  {errors.projectTitle && (
                    <span className="field-error">{errors.projectTitle}</span>
                  )}
                  <div className="field-hint">
                    Название, которое будет использовано для вашего портфолио
                  </div>
                </div>

                {/* Project Description */}
                <div className="field-group">
                  <label htmlFor="project-description" className="field-label">
                    Описание проекта <span className="required">*</span>
                  </label>
                  <textarea
                    id="project-description"
                    value={formData.projectDescription}
                    onChange={(e) => handleChange('projectDescription', e.target.value)}
                    placeholder="Профессиональное портфолио для демонстрации навыков и проектов"
                    className={`field-textarea ${errors.projectDescription ? 'error' : ''}`}
                    disabled={isGeneratingAI}
                    rows={3}
                    maxLength={1000}
                  />
                  {errors.projectDescription && (
                    <span className="field-error">{errors.projectDescription}</span>
                  )}
                  <div className="field-hint">
                    {1000 - formData.projectDescription.length} символов осталось
                  </div>
                </div>

                {/* User Data */}
                <div className="field-group user-data-field">
                  <div className="field-label-row">
                    <label htmlFor="user-data" className="field-label">
                      Ваши данные для AI <span className="required">*</span>
                    </label>
                    <button
                      type="button"
                      onClick={fillExampleData}
                      className="example-button"
                      disabled={isGeneratingAI}
                    >
                      📝 Пример
                    </button>
                  </div>
                  <textarea
                    id="user-data"
                    value={formData.userData}
                    onChange={(e) => handleChange('userData', e.target.value)}
                    placeholder="Введите информацию о себе: имя, специализация, навыки, опыт работы, образование, проекты, контакты..."
                    className={`field-textarea large ${errors.userData ? 'error' : ''}`}
                    disabled={isGeneratingAI}
                    rows={12}
                    maxLength={5000}
                  />
                  {errors.userData && (
                    <span className="field-error">{errors.userData}</span>
                  )}
                  <div className="field-hint">
                    <div className="hint-row">
                      <span>Чем больше информации, тем лучше результат</span>
                      <span>{5000 - formData.userData.length} символов осталось</span>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          ) : (
            <div className="no-access-message">
              <div className="no-access-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <h3>AI генерация недоступна</h3>
              <p>
                {!isPremium 
                  ? 'Для использования AI генерации нужна Premium подписка'
                  : 'Вы исчерпали дневной лимит AI генераций'
                }
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button
            type="button"
            onClick={handleClose}
            disabled={isGeneratingAI}
            className="modal-button secondary"
          >
            Отмена
          </button>
          {canUseAI && (
            <button
              onClick={handleSubmit}
              disabled={!formData.projectTitle.trim() || !formData.projectDescription.trim() || !formData.userData.trim()}
              className="modal-button primary ai-button"
            >
              <>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                    <path d="M2 17l10 5 10-5"></path>
                    <path d="M2 12l10 5 10-5"></path>
                  </svg>
                  🤖 Создать с AI
                </>
            </button>
          )}
        </div>
      </div>
    </div>
  );
} 