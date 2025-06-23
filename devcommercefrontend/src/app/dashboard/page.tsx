'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import './style.scss';
import SimpleLoader from '../../components/simple-loader';

export default function Dashboard() {
  const { user, isAuthenticated, isLoading, logout, updateProfile, verifyEmail, resendVerificationCode } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
  });
  const [verificationCode, setVerificationCode] = useState('');
  const [showVerification, setShowVerification] = useState(false);
  const [message, setMessage] = useState('');

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

  const handleLogout = useCallback(async () => {
    try {
      await logout();
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }, [logout, router]);

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

  const handleVerifyEmail = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await verifyEmail(verificationCode);
      setShowVerification(false);
      setVerificationCode('');
      setMessage('Email verified successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(`Error: ${error}`);
      setTimeout(() => setMessage(''), 3000);
    }
  }, [verificationCode, verifyEmail]);

  const handleResendCode = useCallback(async () => {
    try {
      await resendVerificationCode();
      setMessage('Verification code sent to your email!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(`Error: ${error}`);
      setTimeout(() => setMessage(''), 3000);
    }
  }, [resendVerificationCode]);

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

  return (
    <div className="dashboard">
      <div className="dashboard-container">
        <header className="dashboard-header">
          <h1>Welcome to Your Dashboard</h1>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </header>

        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}

        <div className="dashboard-content">
          <div className="profile-section">
            <div className="profile-card">
              <h2>Profile Information</h2>
              
              {!user.is_email_verified && (
                <div className="email-verification-notice">
                  <p>⚠️ Your email is not verified</p>
                  <button onClick={() => setShowVerification(true)} className="verify-btn">
                    Verify Email
                  </button>
                  <button onClick={handleResendCode} className="resend-btn">
                    Resend Code
                  </button>
                </div>
              )}

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

          <div className="stats-section">
            <div className="stats-card">
              <h3>Account Statistics</h3>
              <div className="stat-item">
                <span className="stat-label">Account Status:</span>
                <span className={`stat-value ${user.is_email_verified ? 'verified' : 'unverified'}`}>
                  {user.is_email_verified ? 'Verified' : 'Unverified'}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Last Updated:</span>
                <span className="stat-value">{new Date(user.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>

        {showVerification && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Verify Your Email</h3>
              <p>Enter the verification code sent to your email:</p>
              <form onSubmit={handleVerifyEmail}>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  required
                />
                <div className="modal-actions">
                  <button type="submit" className="verify-btn">Verify</button>
                  <button type="button" onClick={() => setShowVerification(false)} className="cancel-btn">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 