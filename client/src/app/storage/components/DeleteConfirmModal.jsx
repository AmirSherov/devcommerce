import React from 'react';
import './DeleteConfirmModal.scss';

const DeleteConfirmModal = ({ open, onClose, onConfirm, title = 'Удалить элемент', description = 'Вы уверены, что хотите удалить этот элемент? Это действие необратимо.' }) => {
  if (!open) return null;

  return (
    <div className="delete-modal-overlay" onClick={onClose}>
      <div className="delete-modal" onClick={e => e.stopPropagation()}>
        <div className="delete-modal-header">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#ff6b6b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h3>{title}</h3>
        </div>
        <div className="delete-modal-body">
          <p>{description}</p>
        </div>
        <div className="delete-modal-actions">
          <button className="cancel-btn" onClick={onClose}>Отмена</button>
          <button className="delete-btn" onClick={onConfirm}>Удалить</button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmModal; 