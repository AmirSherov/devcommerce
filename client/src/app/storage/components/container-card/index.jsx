import React from 'react';
import Link from 'next/link';
import './style.scss';
import { FaDatabase } from "react-icons/fa";
const ContainerCard = ({ container }) => {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Link href={`/storage/container/${container.id}`} className="container-card">
      <div className="card-content">
        <div className="card-header">
          <div className="container-icon">
          <FaDatabase />
          </div>
          <div className="container-status">
            {container.is_public ? (
              <span className="status-badge public">Публичный</span>
            ) : (
              <span className="status-badge private">Приватный</span>
            )}
          </div>
        </div>

        <div className="card-body">
          <h3 className="container-name">{container.name}</h3>
          
          <div className="container-stats">
            <div className="stat-item">
              <span className="stat-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <span className="stat-value">{container.files_count}</span>
              <span className="stat-label">файлов</span>
            </div>
            
            <div className="stat-item">
              <span className="stat-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M7 10L12 15L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <span className="stat-value">{formatFileSize(container.total_size)}</span>
              <span className="stat-label">размер</span>
            </div>
          </div>

          <div className="container-meta">
            <div className="meta-item">
              <span className="meta-label">Создан:</span>
              <span className="meta-value">
                {new Date(container.created_at).toLocaleDateString('ru-RU', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric'
                })}
              </span>
            </div>
            
            <div className="meta-item">
              <span className="meta-label">Обновлен:</span>
              <span className="meta-value">
                {new Date(container.updated_at).toLocaleDateString('ru-RU', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric'
                })}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ContainerCard; 