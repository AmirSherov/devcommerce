'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { storageAPI } from '../../../../api/storage/api';
import './style.scss';
import SimpleLoader from '@/components/simple-loader';
import ImageCard from './components/ImageCard';
import VideoCard from './components/VideoCard';
import AudioCard from './components/AudioCard';
import FileCard from './components/FileCard';
import DashboardLayout from '@/components/ui/dashboard-layout';
const ContainerPage = () => {
  const params = useParams();
  const router = useRouter();
  const containerId = params.id;

  const [container, setContainer] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    if (containerId) {
      loadContainer();
      loadFiles();
    }
  }, [containerId, currentPage]);

  const loadContainer = async () => {
    try {
      const response = await storageAPI.getContainer(containerId);
      if (response.success) {
        setContainer(response.container);
      } else {
        setError(response.error || 'Контейнер не найден');
      }
    } catch (error) {
      setError('Ошибка загрузки контейнера');
      console.error('Ошибка загрузки контейнера:', error);
    }
  };

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await storageAPI.getContainerFiles(containerId, currentPage, 20);
      
      if (response.success) {
        setFiles(response.files);
        setTotalPages(Math.ceil(response.pagination.total_files / 20));
      } else {
        setError(response.error || 'Ошибка загрузки файлов');
      }
    } catch (error) {
      setError('Ошибка загрузки файлов');
      console.error('Ошибка загрузки файлов:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setUploading(true);
    setError(''); // Очищаем предыдущие ошибки

    try {
      const formData = {
        file: file,
        filename: file.name,
        is_public: false
      };

      const response = await storageAPI.uploadFile(containerId, formData);
      
      if (response.success) {
        // Обновляем список файлов
        loadFiles();
        loadContainer(); // Обновляем статистику контейнера
        setSelectedFile(null);
      } else {
        // Показываем специфическую ошибку с сервера
        setError(response.error || 'Ошибка загрузки файла');
      }
    } catch (error) {
      setError('Ошибка загрузки файла');
      console.error('Ошибка загрузки файла:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      const response = await storageAPI.deleteFile(fileId);
      
      if (response.success) {
        loadFiles();
        loadContainer();
      } else {
        setError(response.error || 'Ошибка удаления файла');
      }
    } catch (error) {
      setError('Ошибка удаления файла');
      console.error('Ошибка удаления файла:', error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileType = (mimeType) => {
    if (mimeType?.startsWith('image/')) return 'image';
    if (mimeType?.startsWith('video/')) return 'video';
    if (mimeType?.startsWith('audio/')) return 'audio';
    return 'file';
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

  if (loading && !container) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <SimpleLoader text="Загрузка контейнера..." fullScreen={true} />
      </div>
    );
  }

  if (error && !container) {
    return (
      <div className="container-page">
        <div className="error-container">
          <div className="error-message">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {error}
          </div>
          <button className="back-button" onClick={() => router.push('/storage')}>
            Вернуться к хранилищу
          </button>
        </div>
      </div>
    );
  }

  return (
   <DashboardLayout activePage="storage">
     <div className="container-page">
      {/* Заголовок контейнера */}
      <div className="container-header">
        <div className="header-content">
          <div className="header-left">
            <button className="back-button" onClick={() => router.push('/storage')}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Назад
            </button>
            
            <div className="container-info">
              <h1 className="container-name">{container?.name}</h1>
              <div className="container-meta">
                <span className="meta-item">
                  <span className="meta-label">Файлов:</span>
                  <span className="meta-value">{container?.files_count}</span>
                </span>
                <span className="meta-item">
                  <span className="meta-label">Размер:</span>
                  <span className="meta-value">{formatFileSize(container?.total_size || 0)}</span>
                </span>
                <span className="meta-item">
                  <span className="meta-label">Статус:</span>
                  <span className={`status-badge ${container?.is_public ? 'public' : 'private'}`}>
                    {container?.is_public ? 'Публичный' : 'Приватный'}
                  </span>
                </span>
              </div>
            </div>
          </div>
          
          <div className="header-right">
            <label className="upload-button">
              <input
                type="file"
                onChange={handleFileUpload}
                disabled={uploading}
                style={{ display: 'none' }}
              />
              {uploading ? (
                <div className="uploading-spinner">
                  <div className="spinner"></div>
                  Загрузка...
                </div>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Загрузить файл
                </>
              )}
            </label>
          </div>
        </div>
      </div>

      {/* Основной контент */}
      <div className="container-content">
        {error && (
          <div className="error-message">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {error}
          </div>
        )}

        {files.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3>В контейнере пока нет файлов</h3>
            <p>Загрузите первый файл, чтобы начать работу</p>
          </div>
        ) : (
          <>
            <div className="files-grid">
              {files.map((file) => {
                const fileType = getFileType(file.mime_type);
                
                switch (fileType) {
                  case 'image':
                    return <ImageCard key={file.id} file={file} onDelete={handleDeleteFile} />;
                  case 'video':
                    return <VideoCard key={file.id} file={file} onDelete={handleDeleteFile} />;
                  case 'audio':
                    return <AudioCard key={file.id} file={file} onDelete={handleDeleteFile} />;
                  default:
                    return <FileCard key={file.id} file={file} onDelete={handleDeleteFile} />;
                }
              })}
            </div>

            {/* Пагинация */}
            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  className="pagination-button"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Назад
                </button>
                
                <div className="pagination-info">
                  Страница {currentPage} из {totalPages}
                </div>
                
                <button 
                  className="pagination-button"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Вперед
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
   </DashboardLayout>
  );
};

export default ContainerPage; 