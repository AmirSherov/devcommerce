'use client';

import { useAuth } from '../../../../contexts/AuthContext';
import { useState } from 'react';
import EmailVerificationModal from './EmailVerificationModal';

interface ProfileHeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function ProfileHeader({ activeTab, onTabChange }: ProfileHeaderProps) {
  const { user } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showVerificationModal, setShowVerificationModal] = useState(false);

  const getInitials = (firstName?: string, lastName?: string): string => {
    const first = firstName?.charAt(0)?.toUpperCase() || '';
    const last = lastName?.charAt(0)?.toUpperCase() || '';
    return first + last || user?.email?.charAt(0)?.toUpperCase() || 'U';
  };

  const tabs = [
    { id: 'overview', name: 'Информация об аккаунте', shortName: 'Инфо' },
    { id: 'projects', name: 'Проекты', shortName: 'Проекты' },
    { id: 'portfolio', name: 'Портфолио', shortName: 'Портфолио' },
    { id: 'devissue', name: 'DevIssue', shortName: 'Issues' }
  ];

  return (
    <div className="bg-gradient-to-br from-black via-gray-900 to-black border-b border-gray-700">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Profile Info */}
        <div className="py-6 sm:py-8">
          <div className="flex flex-col sm:flex-row items-center sm:items-start space-y-6 sm:space-y-0 sm:space-x-8 lg:space-x-16">
            {/* Avatar */}
            <div className="relative flex-shrink-0">
              <div className="w-20 h-20 sm:w-24 sm:h-24 bg-gradient-to-br from-gray-700 to-gray-800 rounded-full flex items-center justify-center text-xl sm:text-2xl font-bold text-white border-2 border-gray-600 shadow-xl">
                {getInitials(user?.first_name, user?.last_name)}
              </div>
              <div className="absolute -bottom-1 -right-1 w-5 h-5 sm:w-6 sm:h-6 bg-gray-700 rounded-full border-2 border-black flex items-center justify-center shadow-lg">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              </div>
            </div>

            {/* User Info */}
            <div className="flex-1 text-center sm:text-left sm:ml-4 lg:ml-8">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-1">
                {user?.full_name || user?.username || 'Пользователь'}
              </h1>
              <p className="text-gray-400 text-base sm:text-lg mb-2">@{user?.username}</p>
              <div className="flex items-center justify-center sm:justify-start text-gray-300 text-sm sm:text-base">
                <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                </svg>
                <span className="truncate">{user?.email}</span>
                
                {/* Email Verification Status */}
                {user?.is_email_verified === false && (
                  <div className="ml-2 flex items-center">
                    <div className="relative group">
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-red-600 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10">
                        Почта не подтверждена
                      </div>
                    </div>
                  </div>
                )}
                
                {user?.is_email_verified === false && (
                  <button
                    onClick={() => setShowVerificationModal(true)}
                    className="ml-3 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded-full font-medium transition-all duration-200 transform hover:scale-105"
                  >
                    Подтвердить
                  </button>
                )}
                
                {user?.is_email_verified === true && (
                  <div className="ml-2 flex items-center">
                    <div className="relative group">
                      <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-green-600 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10">
                        Почта подтверждена
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
              <button className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105">
                <span className="hidden sm:inline">Редактировать профиль</span>
                <span className="sm:hidden">Редактировать</span>
              </button>
              <button className="bg-gray-800 text-white px-4 py-2 rounded-lg font-medium border border-gray-600 hover:bg-gray-700 hover:border-gray-500 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105">
                Настройки
              </button>
            </div>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="relative">
          {/* Desktop Tabs */}
          <div className="hidden sm:flex space-x-0 border-b border-gray-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-4 lg:px-6 py-3 font-medium text-sm lg:text-base border-b-2 transition-all duration-200 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-white text-white bg-gray-800/30'
                    : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500 hover:bg-gray-800/20'
                }`}
                              >
                  <span className="flex items-center space-x-2">
                    <span className="hidden md:inline">{tab.name}</span>
                    <span className="md:hidden">{tab.shortName}</span>
                  </span>
                </button>
            ))}
          </div>

          {/* Mobile Tabs */}
          <div className="sm:hidden">
            {/* Mobile Tabs Trigger */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-800 border border-gray-600 rounded-t-lg text-white font-medium"
            >
              <span className="flex items-center space-x-2">
                <span>{tabs.find(t => t.id === activeTab)?.name}</span>
              </span>
              <svg 
                className={`w-5 h-5 transition-transform duration-200 ${isMenuOpen ? 'rotate-180' : ''}`}
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>

            {/* Mobile Dropdown */}
            {isMenuOpen && (
              <div className="absolute top-full left-0 right-0 bg-gray-800 border border-gray-600 border-t-0 rounded-b-lg shadow-xl z-20">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      onTabChange(tab.id);
                      setIsMenuOpen(false);
                    }}
                    className={`w-full flex items-center space-x-3 px-4 py-3 text-left font-medium transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'text-white bg-gray-700'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  >
                    <span>{tab.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Scrollable Indicator for Desktop */}
          <div className="hidden sm:block absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-500 to-transparent opacity-30"></div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-10 sm:hidden"
          onClick={() => setIsMenuOpen(false)}
        />
      )}

      {/* Email Verification Modal */}
      <EmailVerificationModal
        isOpen={showVerificationModal}
        onClose={() => setShowVerificationModal(false)}
        onSuccess={() => {
          // Refresh user data or show success message
          window.location.reload();
        }}
      />
    </div>
  );
} 