'use client';

import { useState } from 'react';

export default function PortfolioTab() {
  const [portfolioItems] = useState([]); // В будущем получать из API

  const PortfolioCard = ({ 
    title, 
    description, 
    imageUrl, 
    tags, 
    date,
    link 
  }: {
    title: string;
    description: string;
    imageUrl?: string;
    tags: string[];
    date: string;
    link?: string;
  }) => (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden hover:border-gray-700 transition-colors group">
      {/* Image placeholder */}
      <div className="h-48 bg-gray-800 flex items-center justify-center">
        {imageUrl ? (
          <img src={imageUrl} alt={title} className="w-full h-full object-cover" />
        ) : (
          <svg className="w-16 h-16 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
        )}
      </div>
      
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
            {title}
          </h3>
          {link && (
            <button className="text-gray-400 hover:text-white transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
              </svg>
            </button>
          )}
        </div>
        
        <p className="text-gray-400 mb-4 text-sm">{description}</p>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag, index) => (
            <span 
              key={index}
              className="bg-gray-800 text-gray-300 px-2 py-1 rounded text-xs"
            >
              {tag}
            </span>
          ))}
        </div>
        
        <div className="text-sm text-gray-400">
          {date}
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Портфолио</h1>
          <p className="text-gray-400">Ваши лучшие работы и проекты</p>
        </div>
        <button className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
          Добавить работу
        </button>
      </div>

      {/* Categories */}
      <div className="flex items-center space-x-4 mb-8">
        <button className="bg-white text-black px-4 py-2 rounded-lg font-medium">
          Все
        </button>
        <button className="bg-gray-800 border border-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
          Веб-разработка
        </button>
        <button className="bg-gray-800 border border-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
          Дизайн
        </button>
        <button className="bg-gray-800 border border-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
          Мобильные приложения
        </button>
      </div>

      {/* Portfolio Grid */}
      {portfolioItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {portfolioItems.map((item: any, index: number) => (
            <PortfolioCard key={index} {...item} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <svg className="w-24 h-24 mx-auto text-gray-600 mb-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
          <h3 className="text-xl font-bold text-white mb-2">Портфолио пустое</h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Добавьте свои лучшие работы, чтобы продемонстрировать свои навыки и привлечь потенциальных клиентов или работодателей.
          </p>
          <button className="bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            Добавить первую работу
          </button>
        </div>
      )}
    </div>
  );
} 