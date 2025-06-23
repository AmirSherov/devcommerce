'use client';

import { useAuth } from '../../../../contexts/AuthContext';

interface ProfileHeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function ProfileHeader({ activeTab, onTabChange }: ProfileHeaderProps) {
  const { user } = useAuth();

  const getInitials = (firstName?: string, lastName?: string): string => {
    const first = firstName?.charAt(0)?.toUpperCase() || '';
    const last = lastName?.charAt(0)?.toUpperCase() || '';
    return first + last || user?.email?.charAt(0)?.toUpperCase() || 'U';
  };

  const tabs = [
    { id: 'overview', name: 'Информация об аккаунте'},
    { id: 'projects', name: 'Проекты'},
    { id: 'portfolio', name: 'Портфолио'},
    { id: 'devissue', name: 'DevIssue'}
  ];

  return (
    <div className="bg-black border-b border-gray-800">
      <div className="max-w-6xl mx-auto px-6">
        {/* Profile Info */}
        <div className="py-8">
          <div className="flex items-start space-x-6">
            {/* Avatar */}
            <div className="relative">
              <div className="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center text-2xl font-bold text-white border-2 border-gray-700">
                {getInitials(user?.first_name, user?.last_name)}
              </div>
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gray-700 rounded-full border-2 border-black flex items-center justify-center">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
            </div>

            {/* User Info */}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-white mb-1">
                {user?.full_name || user?.username || 'Пользователь'}
              </h1>
              <p className="text-gray-400 text-lg mb-2">@{user?.username}</p>
              <p className="text-gray-300 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                </svg>
                {user?.email}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Редактировать профиль
              </button>
              <button className="bg-gray-800 text-white px-4 py-2 rounded-lg font-medium border border-gray-700 hover:bg-gray-700 transition-colors">
                Настройки
              </button>
            </div>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="flex space-x-0 border-b border-gray-800">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-white text-white'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
              }`}
            >
              <span className="flex items-center space-x-2">
                <span>{tab.name}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
} 