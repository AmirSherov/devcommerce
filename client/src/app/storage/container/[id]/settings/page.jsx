'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { storageAPI } from '../../../../../api/storage/api';
import { containerSettingsAPI } from '../../../../../api/containersettings/api';
import './style.scss';
import SimpleLoader from '@/components/simple-loader';
import DashboardLayout from '@/components/ui/dashboard-layout';
import ApiDocs from '../components/ApiDocs.jsx';

const ContainerSettingsPage = () => {
  const params = useParams();
  const router = useRouter();
  const containerId = params.id;

  const [container, setContainer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('stats');
  const [apiKey, setApiKey] = useState(null);
  const [stats, setStats] = useState(null);
  const [publicApiStats, setPublicApiStats] = useState(null);

  useEffect(() => {
    if (containerId) {
      loadContainer();
      loadApiKey();
      loadStats();
      loadPublicApiStats();
    }
  }, [containerId]);

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
    } finally {
      setLoading(false);
    }
  };

  const loadApiKey = async () => {
    try {
      const response = await containerSettingsAPI.getPublicApiKey(containerId);
      if (response.success) {
        setApiKey(response.api_key);
      } else {
        console.error('Ошибка загрузки API ключа:', response.error);
      }
    } catch (error) {
      console.error('Ошибка загрузки API ключа:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await containerSettingsAPI.getContainerStats(containerId);
      if (response.success) {
        setStats(response.stats);
      } else {
        console.error('Ошибка загрузки статистики:', response.error);
      }
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  const loadPublicApiStats = async () => {
    try {
      const response = await containerSettingsAPI.getPublicApiStats(containerId);
      if (response.success) {
        setPublicApiStats(response.stats);
      } else {
        console.error('Ошибка загрузки статистики публичного API:', response.error);
      }
    } catch (error) {
      console.error('Ошибка загрузки статистики публичного API:', error);
    }
  };

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

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <SimpleLoader text="Загрузка настроек..." fullScreen={true} />
      </div>
    );
  }

  if (error && !container) {
    return (
      <div className="container-settings-page">
        <div className="error-container">
          <div className="error-message">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {error}
          </div>
          <button className="back-button" onClick={() => router.push(`/storage/container/${containerId}`)}>
            Вернуться к контейнеру
          </button>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout activePage="storage">
      <div className="container-settings-page">
        {/* Заголовок */}
        <div className="settings-header">
          <div className="header-content">
            <div className="header-left">
              <button className="back-button" onClick={() => router.push(`/storage/container/${containerId}`)}>
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
              <h2 className="settings-title">Настройки контейнера</h2>
            </div>
          </div>
        </div>

        {/* Навигация по вкладкам */}
        <div className="settings-navigation">
          <div className="nav-tabs">
            <button 
              className={`nav-tab ${activeTab === 'stats' ? 'active' : ''}`}
              onClick={() => setActiveTab('stats')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3V21H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 9L12 6L16 10L21 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Статистика
            </button>
            
            <button 
              className={`nav-tab ${activeTab === 'api' ? 'active' : ''}`}
              onClick={() => setActiveTab('api')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 13A5 5 0 0 0 20 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M14 17A5 5 0 0 0 4 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M18 7A5 5 0 0 0 8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              API
            </button>
            
            <button 
              className={`nav-tab ${activeTab === 'docs' ? 'active' : ''}`}
              onClick={() => setActiveTab('docs')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Документация
            </button>
          </div>
        </div>

        {/* Контент вкладок */}
        <div className="settings-content">
          {activeTab === 'stats' && (
            <div className="stats-tab">
              {/* Основная статистика */}
              <section className="vertical-section">
                <h2 className="vertical-title">Основная статистика</h2>
                <div className="vertical-items">
                  <div className="vertical-item"><span>Всего файлов:</span> <span>{container?.files_count || 0}</span></div>
                  <div className="vertical-item"><span>Общий размер:</span> <span>{formatFileSize(container?.total_size || 0)}</span></div>
                  <div className="vertical-item"><span>Дата создания:</span> <span>{formatDate(container?.created_at)}</span></div>
                  <div className="vertical-item"><span>Последнее обновление:</span> <span>{formatDate(container?.updated_at)}</span></div>
                </div>
              </section>
              {/* Файлы по типам */}
              <section className="vertical-section">
                <h2 className="vertical-title">Файлы по типам</h2>
                <div className="vertical-items">
                  {stats?.files_by_type && Object.entries(stats.files_by_type).map(([type, count]) => (
                    <div key={type} className="vertical-item">
                      <span>{type}:</span> <span>{count}</span>
                    </div>
                  ))}
                </div>
              </section>
              {/* Топ файлы по размеру */}
              <section className="vertical-section">
                <h2 className="vertical-title">Топ файлы по размеру</h2>
                <div className="vertical-items">
                  {stats?.top_files?.map((file, idx) => (
                    <div key={idx} className="vertical-item">
                      <span>{file.filename}</span> <span>{formatFileSize(file.file_size)}</span> <span>{formatDate(file.uploaded_at)}</span>
                    </div>
                  ))}
                </div>
              </section>
              {/* Последние загрузки */}
              <section className="vertical-section">
                <h2 className="vertical-title">Последние загрузки</h2>
                <div className="vertical-items">
                  {stats?.recent_uploads?.map((file, idx) => (
                    <div key={idx} className="vertical-item">
                      <span>{file.filename}</span> <span>{formatFileSize(file.size)}</span> <span>{formatDate(file.date)}</span>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="api-tab">
              <div className="api-grid">
                {/* API ключ */}
                <div className="api-card api-key">
                  <h3 className="card-title">API ключ</h3>
                  <div className="api-key-content">
                    <div className="key-info">
                      <span className="key-label">API ключ:</span>
                      <div className="key-value">
                        <code className="api-key-code">{apiKey?.api_key}</code>
                        <button className="copy-button">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M16 4H18C19.1046 4 20 4.89543 20 6V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <rect x="8" y="2" width="8" height="4" rx="1" ry="1" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="key-stats">
                      <div className="key-stat">
                        <span className="stat-label">Статус:</span>
                        <span className={`stat-value ${apiKey?.is_active ? 'active' : 'inactive'}`}>
                          {apiKey?.is_active ? 'Активен' : 'Неактивен'}
                        </span>
                      </div>
                      <div className="key-stat">
                        <span className="stat-label">Запросов:</span>
                        <span className="stat-value">{apiKey?.total_requests || 0}</span>
                      </div>
                      <div className="key-stat">
                        <span className="stat-label">Последнее использование:</span>
                        <span className="stat-value">
                          {apiKey?.last_used_at ? formatDate(apiKey.last_used_at) : 'Никогда'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Примеры запросов */}
                <div className="api-card examples">
                  <h3 className="card-title">Примеры запросов</h3>
                  <div className="examples-list">
                    <div className="example-item">
                      <h4 className="example-title">Загрузка файла</h4>
                      <div className="code-block">
                        <div className="code-header">
                          <span className="method">POST</span>
                          <span className="endpoint">/api/public/storage/upload/</span>
                        </div>
                        <pre className="code-content">
{`curl -X POST \\
  -H "Authorization: Bearer ${apiKey?.api_key}" \\
  -F "file=@image.jpg" \\
  https://api.devhub.com/api/public/storage/upload/`}
                        </pre>
                      </div>
                    </div>
                    
                    <div className="example-item">
                      <h4 className="example-title">Получение списка файлов</h4>
                      <div className="code-block">
                        <div className="code-header">
                          <span className="method">GET</span>
                          <span className="endpoint">/api/public/storage/files/</span>
                        </div>
                        <pre className="code-content">
{`curl -X GET \\
  -H "Authorization: Bearer ${apiKey?.api_key}" \\
  https://api.devhub.com/api/public/storage/files/`}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Статистика API */}
                <div className="api-card api-stats">
                  <h3 className="card-title">Статистика API</h3>
                  <div className="api-stats-grid">
                    <div className="api-stat-item">
                      <span className="stat-label">Всего запросов</span>
                      <span className="stat-value">{publicApiStats?.total_requests || 0}</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Успешных запросов</span>
                      <span className="stat-value">{publicApiStats?.successful_requests || 0}</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Процент успеха</span>
                      <span className="stat-value">{publicApiStats?.success_rate || 0}%</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Среднее время ответа</span>
                      <span className="stat-value">{publicApiStats?.average_response_time || 0}ms</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Загружено файлов</span>
                      <span className="stat-value">{publicApiStats?.files_uploaded || 0}</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Скачано файлов</span>
                      <span className="stat-value">{publicApiStats?.files_downloaded || 0}</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Общий размер загрузок</span>
                      <span className="stat-value">{publicApiStats?.total_upload_size_mb || 0} MB</span>
                    </div>
                    <div className="api-stat-item">
                      <span className="stat-label">Общий размер скачиваний</span>
                      <span className="stat-value">{publicApiStats?.total_download_size_mb || 0} MB</span>
                    </div>
                  </div>
                </div>

                {/* Популярные эндпоинты */}
                <div className="api-card popular-endpoints">
                  <h3 className="card-title">Популярные эндпоинты</h3>
                  <div className="endpoints-list">
                    {publicApiStats?.popular_endpoints?.map((endpoint, index) => (
                      <div key={index} className="endpoint-stat">
                        <span className="endpoint-path">{endpoint.endpoint}</span>
                        <span className="endpoint-count">{endpoint.count} запросов</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Настройки доступа */}
                <div className="api-card access-settings">
                  <h3 className="card-title">Настройки доступа</h3>
                  <div className="settings-list">
                    <div className="setting-item">
                      <div className="setting-info">
                        <span className="setting-label">Публичный доступ</span>
                        <span className="setting-description">Разрешить публичный доступ к файлам</span>
                      </div>
                      <label className="toggle-switch">
                        <input 
                          type="checkbox" 
                          checked={container?.is_public || false} 
                          readOnly 
                        />
                        <span className="toggle-slider"></span>
                      </label>
                    </div>
                    
                    <div className="setting-item">
                      <div className="setting-info">
                        <span className="setting-label">Лимит запросов</span>
                        <span className="setting-description">Максимум запросов в час</span>
                      </div>
                      <input type="number" className="setting-input" defaultValue={publicApiStats?.rate_limit_per_hour || 1000} min="100" max="10000" />
                    </div>
                    
                    <div className="setting-item">
                      <div className="setting-info">
                        <span className="setting-label">Максимальный размер файла</span>
                        <span className="setting-description">Максимальный размер загружаемого файла</span>
                      </div>
                      <input type="number" className="setting-input" defaultValue={publicApiStats?.max_file_size_mb || 100} min="1" max="1000" />
                      <span className="setting-unit">MB</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'docs' && (
            <ApiDocs apiKey={apiKey} limits={publicApiStats} />
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ContainerSettingsPage; 