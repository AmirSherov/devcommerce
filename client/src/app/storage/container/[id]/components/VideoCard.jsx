'use client';
import React, { useState, useRef } from 'react';
import DeleteConfirmModal from '../../../components/DeleteConfirmModal.jsx';
import './VideoCard.scss';

const VideoCard = ({ file, onDelete }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const videoRef = useRef(null);

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

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleVideoEnded = () => {
    setIsPlaying(false);
  };

  return (
    <>
      <div className="video-card">
        <div className="video-preview">
          <video
            ref={videoRef}
            src={file.file_url}
            className="preview-video"
            onEnded={handleVideoEnded}
            preload="metadata"
          />
          
          <div className="video-overlay">
            <button 
              className="play-button"
              onClick={togglePlay}
            >
              {isPlaying ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                  <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="5,3 19,12 5,21" fill="currentColor"/>
                </svg>
              )}
            </button>
            
            <button 
              className="menu-button"
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
        
        <div className="video-info">
          <h4 className="video-name">{file.filename}</h4>
          <div className="video-meta">
            <span className="video-size">{formatFileSize(file.file_size)}</span>
            <span className="video-date">{formatDate(file.created_at)}</span>
          </div>
        </div>
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
                <video
                  src={file.file_url}
                  controls
                  className="modal-video"
                />
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
        title="Удалить видео"
        description={`Вы уверены, что хотите удалить файл "${file.filename}"? Это действие необратимо.`}
      />
    </>
  );
};

export default VideoCard; 