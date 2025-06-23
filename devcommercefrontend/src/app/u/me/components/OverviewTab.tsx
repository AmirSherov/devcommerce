'use client';

import { useAuth } from '../../../../contexts/AuthContext';

export default function OverviewTab() {
  const { user } = useAuth();

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const StatCard = ({ title, value, description }: { 
    title: string; 
    value: string; 
    description?: string;
  }) => (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors">
      <h3 className="text-white font-medium text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-white mb-1">{value}</p>
      {description && <p className="text-gray-400 text-xs">{description}</p>}
    </div>
  );

  const InfoRow = ({ label, value }: { label: string; value: string }) => (
    <div className="flex justify-between py-3 border-b border-gray-800 last:border-b-0">
      <span className="text-gray-400">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Account Info Card */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg">
            <div className="p-6 border-b border-gray-800">
              <h2 className="text-xl font-bold text-white flex items-center">
                Информация об аккаунте
              </h2>
            </div>
            <div className="p-6">
              <div className="space-y-0">
                <InfoRow label="Полное имя" value={user?.full_name || 'Не указано'} />
                <InfoRow label="Имя пользователя" value={user?.username || 'Не указано'} />
                <InfoRow label="Email" value={user?.email || 'Не указано'} />
                <InfoRow label="Дата регистрации" value={user?.created_at ? formatDate(user.created_at) : 'Не указано'} />
                <InfoRow label="Статус email" value={user?.is_email_verified ? 'Подтвержден' : 'Не подтвержден'} />
                <InfoRow label="Роль" value={user?.role || 'Пользователь'} />
              </div>
            </div>
          </div>

          {/* Activity Card */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg">
            <div className="p-6 border-b border-gray-800">
              <h2 className="text-xl font-bold text-white flex items-center">
                Активность аккаунта
              </h2>
            </div>
            <div className="p-6">
              <div className="text-center py-12">
                <p className="text-gray-400">Данные об активности пока отсутствуют</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Stats */}
          <div className="space-y-4">
            <StatCard 
              title="Проекты" 
              value="0" 
              description="Создано проектов"
            />
            <StatCard 
              title="Портфолио" 
              value="0" 
              description="Работ в портфолио"
            />
            <StatCard 
              title="DevIssues" 
              value="0" 
              description="Открытых тикетов"
            />
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h3 className="text-white font-bold mb-4">Быстрые действия</h3>
            <div className="space-y-3">
              <button className="w-full bg-white text-black py-2 px-4 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Создать проект
              </button>
              <button className="w-full bg-gray-800 text-white py-2 px-4 rounded-lg font-medium border border-gray-700 hover:bg-gray-700 transition-colors">
                Добавить в портфолио
              </button>
              <button className="w-full bg-gray-800 text-white py-2 px-4 rounded-lg font-medium border border-gray-700 hover:bg-gray-700 transition-colors">
                Создать DevIssue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 