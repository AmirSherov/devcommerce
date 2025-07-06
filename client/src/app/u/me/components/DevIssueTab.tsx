'use client';

import { useState } from 'react';

export default function DevIssueTab() {
  const [issues] = useState([]); // В будущем получать из API
  const [activeFilter, setActiveFilter] = useState('all');

  const IssueCard = ({ 
    title, 
    description, 
    status, 
    priority, 
    assignee,
    createdAt,
    labels 
  }: {
    title: string;
    description: string;
    status: 'open' | 'in-progress' | 'closed';
    priority: 'low' | 'medium' | 'high' | 'critical';
    assignee?: string;
    createdAt: string;
    labels: string[];
  }) => {
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'open': return 'bg-green-600';
        case 'in-progress': return 'bg-yellow-600';
        case 'closed': return 'bg-purple-600';
        default: return 'bg-gray-600';
      }
    };

    const getPriorityColor = (priority: string) => {
      switch (priority) {
        case 'critical': return 'text-red-400';
        case 'high': return 'text-orange-400';
        case 'medium': return 'text-yellow-400';
        case 'low': return 'text-green-400';
        default: return 'text-gray-400';
      }
    };

    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-bold text-white hover:text-blue-400 cursor-pointer pr-4">
            {title}
          </h3>
          <div className="flex items-center space-x-2 flex-shrink-0">
            <span className={`w-3 h-3 rounded-full ${getStatusColor(status)}`}></span>
            <span className="text-sm text-gray-400">{status}</span>
          </div>
        </div>
        
        <p className="text-gray-400 mb-4 text-sm line-clamp-2">{description}</p>
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className={`text-sm font-medium ${getPriorityColor(priority)}`}>
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </span>
            {assignee && (
              <span className="text-sm text-gray-400">
                @{assignee}
              </span>
            )}
          </div>
          <span className="text-sm text-gray-400">{createdAt}</span>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {labels.map((label, index) => (
            <span 
              key={index}
              className="bg-gray-800 text-gray-300 px-2 py-1 rounded text-xs"
            >
              {label}
            </span>
          ))}
        </div>
      </div>
    );
  };

  const filters = [
    { id: 'all', name: 'Все', count: 0 },
    { id: 'open', name: 'Открытые', count: 0 },
    { id: 'in-progress', name: 'В работе', count: 0 },
    { id: 'closed', name: 'Закрытые', count: 0 }
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">DevIssues</h1>
          <p className="text-gray-400">Отслеживайте баги, задачи и улучшения</p>
        </div>
        <button className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
          Новый Issue
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-2">
          {filters.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setActiveFilter(filter.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeFilter === filter.id
                  ? 'bg-white text-black'
                  : 'bg-gray-800 border border-gray-700 text-white hover:bg-gray-700'
              }`}
            >
              {filter.name} ({filter.count})
            </button>
          ))}
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Поиск issues..."
            className="bg-gray-900 border border-gray-800 text-white px-4 py-2 rounded-lg focus:border-gray-600 focus:outline-none"
          />
          <button className="bg-gray-800 border border-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
            Фильтры
          </button>
        </div>
      </div>

      {/* Issues List */}
      {issues.length > 0 ? (
        <div className="space-y-4">
          {issues.map((issue: any, index: number) => (
            <IssueCard key={index} {...issue} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <svg className="w-24 h-24 mx-auto text-gray-600 mb-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <h3 className="text-xl font-bold text-white mb-2">Нет активных issues</h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Создайте первый issue для отслеживания багов, задач или предложений по улучшению ваших проектов.
          </p>
          <button className="bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            Создать первый Issue
          </button>
        </div>
      )}

      {/* Quick Stats */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white mb-1">0</div>
          <div className="text-sm text-gray-400">Всего Issues</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400 mb-1">0</div>
          <div className="text-sm text-gray-400">Открытые</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-400 mb-1">0</div>
          <div className="text-sm text-gray-400">В работе</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-400 mb-1">0</div>
          <div className="text-sm text-gray-400">Закрытые</div>
        </div>
      </div>
    </div>
  );
} 