'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import './style.scss';
import SimpleLoader from '../../components/simple-loader';
import DashboardLayout from '../../components/ui/dashboard-layout';

export default function Dashboard() {
  const { user, isAuthenticated, isLoading, updateProfile } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
  });

  const [message, setMessage] = useState('');
  const [activeSection, setActiveSection] = useState('dashboard');

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (user) {
      setEditForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
      });
    }
  }, [user]);

  const handleUpdateProfile = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await updateProfile(editForm);
      setIsEditing(false);
      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(`Error: ${error}`);
      setTimeout(() => setMessage(''), 3000);
    }
  }, [editForm, updateProfile]);

  const handleEditFormChange = useCallback((field: string, value: string) => {
    setEditForm(prev => ({ ...prev, [field]: value }));
  }, []);

  // Показываем лоадер при загрузке
  if (isLoading) {
    return <SimpleLoader text="Загрузка..." />;
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'profile':
        return (
          <div className="profile-section">
            <div className="profile-card">
              <h2>Profile Information</h2>
              {!isEditing ? (
                <div className="profile-info">
                  <div className="info-item">
                    <label>Email:</label>
                    <span>{user.email}</span>
                    {user.is_email_verified && <span className="verified">✓ Verified</span>}
                  </div>
                  <div className="info-item">
                    <label>Username:</label>
                    <span>{user.username}</span>
                  </div>
                  <div className="info-item">
                    <label>First Name:</label>
                    <span>{user.first_name || 'Not set'}</span>
                  </div>
                  <div className="info-item">
                    <label>Last Name:</label>
                    <span>{user.last_name || 'Not set'}</span>
                  </div>
                  <div className="info-item">
                    <label>Full Name:</label>
                    <span>{user.full_name || 'Not set'}</span>
                  </div>
                  <div className="info-item">
                    <label>Member Since:</label>
                    <span>{new Date(user.created_at).toLocaleDateString()}</span>
                  </div>
                  
                  <button onClick={() => setIsEditing(true)} className="edit-btn">
                    Edit Profile
                  </button>
                </div>
              ) : (
                <form onSubmit={handleUpdateProfile} className="edit-form">
                  <div className="form-group">
                    <label>Username:</label>
                    <input
                      type="text"
                      value={editForm.username}
                      onChange={(e) => handleEditFormChange('username', e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>First Name:</label>
                    <input
                      type="text"
                      value={editForm.first_name}
                      onChange={(e) => handleEditFormChange('first_name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Last Name:</label>
                    <input
                      type="text"
                      value={editForm.last_name}
                      onChange={(e) => handleEditFormChange('last_name', e.target.value)}
                    />
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="save-btn">Save Changes</button>
                    <button type="button" onClick={() => setIsEditing(false)} className="cancel-btn">
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        );
      case 'settings':
        return (
          <div className="settings-section">
            <h2>Settings</h2>
            <p>Settings content coming soon...</p>
          </div>
        );
      default:
        return (
          <div className="dashboard-overview">
            <h1>Добро пожаловать в ваш Dashboard!</h1>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Профиль</h3>
                <p>Статус: {user.is_email_verified ? 'Верифицирован' : 'Не верифицирован'}</p>
              </div>
              <div className="stat-card">
                <h3>Участник с</h3>
                <p>{new Date(user.created_at).toLocaleDateString()}</p>
              </div>
              <div className="stat-card">
                <h3>Email</h3>
                <p>{user.email}</p>
              </div>
              <div className="stat-card">
                <h3>Имя пользователя</h3>
                <p>{user.username}</p>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <DashboardLayout activePage="dashboard">
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'} mb-4 p-4 rounded-lg`}>
          {message}
        </div>
      )}
      
      {renderContent()}
    </DashboardLayout>
  );
} 