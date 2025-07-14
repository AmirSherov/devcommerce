import React, { useState } from 'react';
import DeleteConfirmModal from '../../../components/DeleteConfirmModal.jsx';
import './FileCard.scss';

const FileCard = ({ file, onDelete }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDelete = () => {
    setShowMenu(false);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    setShowDeleteModal(false);
    onDelete(file.id);
  };

  const getFileIcon = (mimeType, filename) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    
    // Документы
    if (mimeType?.startsWith('application/pdf')) {
      return (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M9 13H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M9 17H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M9 9H10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      );
    }
    
    if (mimeType?.startsWith('application/msword') || mimeType?.startsWith('application/vnd.openxmlformats-officedocument.wordprocessingml') || extension === 'doc' || extension === 'docx') {
      return (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8 13L10.5 16L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      );
    }
    
    if (mimeType?.startsWith('application/vnd.ms-excel') || mimeType?.startsWith('application/vnd.openxmlformats-officedocument.spreadsheetml') || extension === 'xls' || extension === 'xlsx') {
      return (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8 13L10.5 16L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8 9H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      );
    }
    
    if (mimeType?.startsWith('application/vnd.ms-powerpoint') || mimeType?.startsWith('application/vnd.openxmlformats-officedocument.presentationml') || extension === 'ppt' || extension === 'pptx') {
      return (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8 13L10.5 16L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8 9H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      );
    }
    
    // Архивы
    if (mimeType?.startsWith('application/zip') || mimeType?.startsWith('application/x-rar') || extension === 'zip' || extension === 'rar' || extension === '7z') {
      return (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M7 10L12 15L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      );
    }
    
    // Текстовые файлы
    if (mimeType?.startsWith('text/') || extension === 'txt' || extension === 'md' || extension === 'json' || extension === 'xml' || extension === 'html' || extension === 'css' || extension === 'js') {
      return (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M10 9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      );
    }
    
    // По умолчанию
    return (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    );
  };

  return (
    <>
      <div className="file-card">
        <div className="file-header">
          <div className="file-icon">
            {getFileIcon(file.mime_type, file.filename)}
          </div>
          <div className="file-actions">
            <button 
              className="action-button menu"
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              title="Меню"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="1" fill="currentColor"/>
                <circle cx="6" cy="12" r="1" fill="currentColor"/>
                <circle cx="18" cy="12" r="1" fill="currentColor"/>
              </svg>
            </button>
            
            {showMenu && (
              <div className="menu-dropdown">
                <a 
                  href={file.file_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="menu-item"
                  onClick={() => setShowMenu(false)}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Скачать
                </a>
                <button 
                  className="menu-item"
                  onClick={() => {
                    setShowMenu(false);
                    setShowModal(true);
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 16H6L14 8L6 8L6 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M22 21V19C22 17.9391 21.5786 16.9217 20.8284 16.1716C20.0783 15.4214 19.0609 15 18 15H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M16 3H13V6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M22 3L19 6L22 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Информация
                </button>
                <button 
                  className="menu-item delete"
                  onClick={handleDelete}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Удалить
                </button>
              </div>
            )}
          </div>
        </div>
        
        <div className="file-body">
          <h3 className="file-name">{file.filename}</h3>
          <div className="file-meta">
            <span className="file-size">{formatFileSize(file.file_size)}</span>
            <span className="file-date">{formatDate(file.created_at)}</span>
          </div>
        </div>
        
        {file.file_url && (
          <div className="file-footer">
            <a 
              href={file.file_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="download-link"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Скачать
            </a>
          </div>
        )}
      </div>

      {/* Модальное окно с информацией */}
      {showModal && (
        <div 
          className="file-modal-overlay" 
          onClick={() => setShowModal(false)}
          onKeyDown={(e) => e.key === 'Escape' && setShowModal(false)}
          tabIndex={0}
        >
          <div className="file-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Информация о файле</h3>
              <button 
                className="close-button"
                onClick={() => setShowModal(false)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
            
            <div className="modal-content">
              <div className="file-preview">
                <div className="file-icon-large">
                  {getFileIcon(file.mime_type, file.filename)}
                </div>
                <h4 className="file-name-large">{file.filename}</h4>
              </div>
              
              <div className="file-details">
                <div className="detail-item">
                  <span className="detail-label">Имя файла:</span>
                  <span className="detail-value">{file.filename}</span>
                </div>
                
                <div className="detail-item">
                  <span className="detail-label">Размер:</span>
                  <span className="detail-value">{formatFileSize(file.file_size)}</span>
                </div>
                
                <div className="detail-item">
                  <span className="detail-label">Тип:</span>
                  <span className="detail-value">{file.mime_type}</span>
                </div>
                
                <div className="detail-item">
                  <span className="detail-label">Загружен:</span>
                  <span className="detail-value">{formatDate(file.created_at)}</span>
                </div>
                
                <div className="detail-item">
                  <span className="detail-label">Статус:</span>
                  <span className={`detail-value status-${file.is_public ? 'public' : 'private'}`}>
                    {file.is_public ? 'Публичный' : 'Приватный'}
                  </span>
                </div>
              </div>
            </div>
            

          </div>
        </div>
      )}

      {/* Модальное окно подтверждения удаления */}
      <DeleteConfirmModal
        open={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={confirmDelete}
        title="Удалить файл"
        description={`Вы уверены, что хотите удалить файл "${file.filename}"? Это действие необратимо.`}
      />
    </>
  );
};

export default FileCard; 