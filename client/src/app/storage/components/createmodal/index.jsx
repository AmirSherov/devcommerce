import React, { useState } from 'react';
import { storageAPI } from '../../../../api/storage/api';
import './style.scss';

const CreateContainerModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    is_public: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Название контейнера обязательно');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await storageAPI.createContainer(formData);
      
      if (response.success) {
        onSuccess(response.container);
        handleClose();
      } else {
        setError(response.error || 'Ошибка создания контейнера');
      }
    } catch (error) {
      setError(error.message || 'Ошибка создания контейнера');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ name: '', is_public: false });
    setError('');
    setLoading(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="create-container-modal-overlay" onClick={handleClose}>
      <div className="create-container-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Создать новый контейнер</h2>
          <button className="close-button" onClick={handleClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name">Название контейнера</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Введите название контейнера"
              className="form-input"
              disabled={loading}
            />
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_public"
                checked={formData.is_public}
                onChange={handleInputChange}
                className="checkbox-input"
                disabled={loading}
              />
              <span className="checkbox-custom"></span>
              <span className="checkbox-text">Публичный контейнер</span>
            </label>
            <p className="checkbox-description">
              Публичные контейнеры доступны для просмотра всем пользователям
            </p>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              className="cancel-button"
              onClick={handleClose}
              disabled={loading}
            >
              Отмена
            </button>
            <button
              type="submit"
              className="create-button"
              disabled={loading || !formData.name.trim()}
            >
              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  Создание...
                </div>
              ) : (
                'Создать контейнер'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateContainerModal; 