'use client';

import React, { useState, useEffect } from 'react';
import { storageAPI } from '../../api/storage/api';
import CreateContainerModal from './components/createmodal';
import ContainerCard from './components/container-card';
import './style.scss';
import SimpleLoader from '@/components/simple-loader';
import { PiShippingContainerBold } from "react-icons/pi";
import DashboardLayout from '@/components/ui/dashboard-layout';
const StoragePage = () => {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadContainers();
    loadStats();
  }, []);

  const loadContainers = async () => {
    try {
      setLoading(true);
      const response = await storageAPI.getContainers();
      
      if (response.success) {
        setContainers(response.containers);
      } else {
        setError(response.error || 'Ошибка загрузки контейнеров');
      }
    } catch (error) {
      setError('Ошибка загрузки контейнеров');
      console.error('Ошибка загрузки контейнеров:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await storageAPI.getStorageStats();
      if (response.success) {
        setStats(response.stats);
      } else {
        console.error('Ошибка загрузки статистики:', response.error);
      }
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  const handleCreateContainer = (newContainer) => {
    setContainers(prev => [newContainer, ...prev]);
    loadStats(); // Обновляем статистику
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
      <SimpleLoader text="Загрузка хранилища..." fullScreen={true} />
    </div>
    );
  }

  return (
    <DashboardLayout activePage="storage">
        <div className="storage-page">
      {/* Заголовок и навигация */}
      <div className="storage-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="page-title">Хранилище</h1>
            <p className="page-description">
              Управляйте вашими файлами и контейнерами
            </p>
          </div>
          
          <div className="header-right">
            <button 
              className="create-button"
              onClick={() => setShowModal(true)}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Создать контейнер
            </button>
          </div>
        </div>

        {/* Статистика */}
        {stats && (
          <div className="storage-stats">
            <div className="stat-card">
              <div className="stat-icon">
              <PiShippingContainerBold />
              </div>
              <div className="stat-content">
                <div className="stat-value">{stats.total_containers}</div>
                <div className="stat-label">Контейнеров</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{stats.total_files}</div>
                <div className="stat-label">Файлов</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M7 10L12 15L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-value">{formatFileSize(stats.total_size_mb * 1024 * 1024)}</div>
                <div className="stat-label">Общий размер</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Основной контент */}
      <div className="storage-content">
        {error && (
          <div className="error-message">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {error}
          </div>
        )}

        {containers.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 7C3 5.89543 3.89543 5 5 5H19C20.1046 5 21 5.89543 21 7V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" strokeWidth="2"/>
                <path d="M3 7L12 13L21 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3>У вас пока нет контейнеров</h3>
            <p>Создайте первый контейнер для хранения файлов</p>
            <button 
              className="create-first-button"
              onClick={() => setShowModal(true)}
            >
              Создать контейнер
            </button>
          </div>
        ) : (
          <div className="containers-grid">
            {containers.map((container) => (
              <ContainerCard key={container.id} container={container} />
            ))}
          </div>
        )}
      </div>

      {/* Модальное окно создания контейнера */}
      <CreateContainerModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleCreateContainer}
      />
    </div>
    </DashboardLayout>
  );
};

export default StoragePage; 