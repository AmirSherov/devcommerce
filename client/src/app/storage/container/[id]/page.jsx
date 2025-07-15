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
            <div className="header-actions">
              <button 
                className="settings-button"
                onClick={() => router.push(`/storage/container/${containerId}/settings`)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.79 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.257 9.77251 19.9887C9.5799 19.7204 9.31074 19.5189 9 19.41C8.69838 19.2769 8.36381 19.2372 8.03941 19.296C7.71502 19.3548 7.41568 19.5095 7.18 19.74L7.12 19.8C6.93425 19.986 6.71368 20.1335 6.47088 20.2341C6.22808 20.3348 5.96783 20.3866 5.705 20.3866C5.44217 20.3866 5.18192 20.3348 4.93912 20.2341C4.69632 20.1335 4.47575 19.986 4.29 19.8C4.10405 19.6143 3.95653 19.3937 3.85588 19.1509C3.75523 18.9081 3.70343 18.6478 3.70343 18.385C3.70343 18.1222 3.75523 17.8619 3.85588 17.6191C3.95653 17.3763 4.10405 17.1557 4.29 16.97L4.35 16.91C4.58054 16.6743 4.73519 16.375 4.79399 16.0506C4.8528 15.7262 4.81312 15.3916 4.68 15.09C4.55324 14.7942 4.34276 14.542 4.07447 14.3643C3.80618 14.1866 3.49179 14.0913 3.17 14.09H3C2.46957 14.09 1.96086 13.8793 1.58579 13.5042C1.21071 13.1291 1 12.6204 1 12.09C1 11.5596 1.21071 11.0409 1.58579 10.6658C1.96086 10.2907 2.46957 10.08 3 10.08H3.09C3.42099 10.0723 3.743 9.96512 4.0113 9.77251C4.2796 9.5799 4.4811 9.31074 4.59 9C4.72312 8.69838 4.7628 8.36381 4.704 8.03941C4.6452 7.71502 4.49054 7.41568 4.26 7.18L4.2 7.12C4.01405 6.93425 3.86653 6.71368 3.76588 6.47088C3.66523 6.22808 3.61343 5.96783 3.61343 5.705C3.61343 5.44217 3.66523 5.18192 3.76588 4.93912C3.86653 4.69632 4.01405 4.47575 4.2 4.29C4.38575 4.10405 4.60632 3.95653 4.84912 3.85588C5.09192 3.75523 5.35217 3.70343 5.615 3.70343C5.87783 3.70343 6.13808 3.75523 6.38088 3.85588C6.62368 3.95653 6.84425 4.10405 7.03 4.29L7.09 4.35C7.32568 4.58054 7.62502 4.73519 7.94941 4.79399C8.27381 4.8528 8.60838 4.81312 8.91 4.68H9C9.29577 4.55324 9.54802 4.34276 9.72569 4.07447C9.90337 3.80618 9.99872 3.49179 10 3.17V3C10 2.46957 10.2107 1.96086 10.5858 1.58579C10.9609 1.21071 11.4696 1 12 1C12.5304 1 13.0391 1.21071 13.4142 1.58579C13.7893 1.96086 14 2.46957 14 3V3.09C14.0013 3.41179 14.0966 3.72618 14.2743 3.99447C14.452 4.26276 14.7042 4.55324 15 4.68C15.3016 4.81312 15.6362 4.8528 15.9606 4.79399C16.285 4.73519 16.5843 4.58054 16.82 4.35L16.88 4.29C17.0657 4.10405 17.2863 3.95653 17.5291 3.85588C17.7719 3.75523 18.0322 3.70343 18.295 3.70343C18.5578 3.70343 18.8181 3.75523 19.0609 3.85588C19.3037 3.95653 19.5243 4.10405 19.71 4.29C19.896 4.47575 20.0435 4.69632 20.1441 4.93912C20.2448 5.18192 20.2966 5.44217 20.2966 5.705C20.2966 5.96783 20.2448 6.22808 20.1441 6.47088C20.0435 6.71368 19.896 6.93425 19.71 7.12L19.65 7.18C19.4195 7.41568 19.2648 7.71502 19.206 8.03941C19.1472 8.36381 19.1869 8.69838 19.32 9V9.09C19.4468 9.38577 19.6572 9.63802 19.9255 9.81569C20.1938 9.99337 20.5082 10.0887 20.83 10.09H21C21.5304 10.09 22.0391 10.3007 22.4142 10.6758C22.7893 11.0409 23 11.5496 23 12.08C23 12.6104 22.7893 13.1191 22.4142 13.4942C22.0391 13.8693 21.5304 14.08 21 14.08H20.91C20.5882 14.0813 20.2738 14.1766 20.0055 14.3543C19.7372 14.532 19.4468 14.7842 19.32 15.08L19.4 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Настройки
              </button>
              
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