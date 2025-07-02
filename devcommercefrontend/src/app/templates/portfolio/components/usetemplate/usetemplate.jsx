'use client';

import { useState } from 'react';
import './style.scss';

export default function UseTemplateModal({ 
  isOpen, 
  onClose, 
  template, 
  onConfirm, 
  isLoading 
}) {
  const [projectData, setProjectData] = useState({
    title: '',
    description: ''
  });

  const [errors, setErrors] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Валидация
    const newErrors = {};
    if (!projectData.title.trim()) {
      newErrors.title = 'Введите название проекта';
    }
    if (!projectData.description.trim()) {
      newErrors.description = 'Введите описание проекта';
    }

    setErrors(newErrors);

    // Если нет ошибок - отправляем данные
    if (Object.keys(newErrors).length === 0) {
      onConfirm(projectData);
    }
  };

  const handleChange = (field, value) => {
    setProjectData(prev => ({
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
    if (!isLoading) {
      setProjectData({ title: '', description: '' });
      setErrors({});
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="use-template-modal-overlay" onClick={handleClose}>
      <div className="use-template-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-content">
            <h2 className="modal-title">Создание проекта</h2>
            <p className="modal-subtitle">
              Используя шаблон: <span className="template-name">{template?.title}</span>
            </p>
          </div>
          <button 
            onClick={handleClose}
            disabled={isLoading}
            className="modal-close-button"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="modal-content">
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
              <div className="template-stats">
                <span>👁️ {template?.views}</span>
                <span>🔥 {template?.uses}</span>
                <span>❤️ {template?.likes}</span>
              </div>
            </div>
          </div>

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
                value={projectData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="Мое портфолио"
                className={`field-input ${errors.title ? 'error' : ''}`}
                disabled={isLoading}
                maxLength={100}
              />
              {errors.title && (
                <span className="field-error">{errors.title}</span>
              )}
              <div className="field-hint">
                Это название будет использовано для вашего портфолио
              </div>
            </div>

            {/* Project Description */}
            <div className="field-group">
              <label htmlFor="project-description" className="field-label">
                Описание проекта <span className="required">*</span>
              </label>
              <textarea
                id="project-description"
                value={projectData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                placeholder="Краткое описание вашего портфолио..."
                className={`field-textarea ${errors.description ? 'error' : ''}`}
                disabled={isLoading}
                rows={4}
                maxLength={500}
              />
              {errors.description && (
                <span className="field-error">{errors.description}</span>
              )}
              <div className="field-hint">
                {500 - projectData.description.length} символов осталось
              </div>
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="modal-footer">
          <button
            type="button"
            onClick={handleClose}
            disabled={isLoading}
            className="modal-button secondary"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={isLoading || !projectData.title.trim() || !projectData.description.trim()}
            className="modal-button primary"
          >
            {isLoading ? (
              <>
                <div className="button-spinner"></div>
                Создаем проект...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22,4 12,14.01 9,11.01"></polyline>
                </svg>
                Создать проект
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
} 