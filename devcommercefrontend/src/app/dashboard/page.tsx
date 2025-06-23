'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import './style.scss';
import SimpleLoader from '../../components/simple-loader';
import { Sidebar, SidebarBody, SidebarLink } from '../../components/ui/sidebar';
import { motion } from 'motion/react';
import { cn } from '../../lib/utils';

// Иконки для sidebar
const DashboardIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7"></rect>
    <rect x="14" y="3" width="7" height="7"></rect>
    <rect x="14" y="14" width="7" height="7"></rect>
    <rect x="3" y="14" width="7" height="7"></rect>
  </svg>
);

const ProfileIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

const SettingsIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m18-4a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
  </svg>
);

const LogoutIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
    <polyline points="16,17 21,12 16,7"></polyline>
    <line x1="21" y1="12" x2="9" y2="12"></line>
  </svg>
);

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

  const links = [
    {
      label: "Dashboard",
      href: "#",
      icon: <DashboardIcon />,
    },
    {
      label: "Profile",
      href: "/u/me",
      icon: <ProfileIcon />,
    },
    {
      label: "Settings",
      href: "#",
      icon: <SettingsIcon />,
    },
    {
      label: "Logout",
      href: "#",
      icon: <LogoutIcon />,
    },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'profile':
        return (
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
    <div className={cn(
      "rounded-md flex flex-col md:flex-row bg-gray-100 dark:bg-neutral-800 w-full flex-1 mx-auto border border-neutral-200 dark:border-neutral-700 overflow-hidden",
      "h-screen"
    )}>
      <Sidebar>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <div key={idx} onClick={() => {
                  if (link.label === 'Logout') {
                    handleLogout();
                  } else if (link.label === 'Profile') {
                    router.push('/u/me');
                  } else {
                    setActiveSection(link.label.toLowerCase());
                  }
                }}>
                  <SidebarLink 
                    link={{
                      ...link,
                      href: '#'
                    }}
                    className={cn(
                      "cursor-pointer hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-lg px-2 py-2",
                      activeSection === link.label.toLowerCase() ? "bg-neutral-200 dark:bg-neutral-700" : ""
                    )}
                  />
                </div>
              ))}
            </div>
          </div>
          <div onClick={() => router.push('/u/me')} className="cursor-pointer">
            <SidebarLink
              link={{
                label: user.username || user.email,
                href: "#",
                icon: (
                  <div className="h-7 w-7 flex-shrink-0 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                    {(user.username || user.email).charAt(0).toUpperCase()}
                  </div>
                ),
              }}
            />
          </div>
        </SidebarBody>
      </Sidebar>
      
      <div className="flex flex-1">
        <div className="p-2 md:p-10 rounded-tl-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 flex flex-col gap-2 flex-1 w-full h-full overflow-y-auto">
          {message && (
            <div className={`message ${message.includes('Error') ? 'error' : 'success'} mb-4 p-4 rounded-lg`}>
              {message}
            </div>
          )}
          
          {renderContent()}

          {showVerification && (
            <div className="verification-modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-neutral-800 p-6 rounded-lg max-w-md w-full mx-4">
                <h3>Verify Your Email</h3>
                <form onSubmit={handleVerifyEmail} className="mt-4">
                  <div className="form-group">
                    <label>Verification Code:</label>
                    <input
                      type="text"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      required
                      className="w-full p-2 border rounded mt-1"
                    />
                  </div>
                  <div className="form-actions mt-4 flex gap-2">
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
    </div>
  );
} 