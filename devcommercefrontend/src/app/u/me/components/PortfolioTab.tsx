'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { portfolioAPI } from '../../../../api/portfolio/api';
import ConfirmModal from '../../../../components/ui/confirm-modal';

interface Portfolio {
  id: string;
  title: string;
  description: string;
  slug: string;
  html_content: string;
  css_content: string;
  js_content: string;
  is_public: boolean;
  tags: string[];
  views: number;
  likes: number;
  created_at: string;
  updated_at: string;
  public_url: string;
  file_urls: {
    html: string;
    css: string;
    js: string;
  };
}

export default function PortfolioTab() {
  const router = useRouter();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [stats, setStats] = useState({
    portfolios_count: 0,
    remaining_slots: 5,
    total_views: 0,
    total_likes: 0
  });

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [portfolioToDelete, setPortfolioToDelete] = useState<Portfolio | null>(null);
  const [isDeletingPortfolio, setIsDeletingPortfolio] = useState(false);

  useEffect(() => {
    loadPortfolios();
    loadStats();
  }, []);

  const loadPortfolios = async () => {
    try {
      setIsLoading(true);
      const response = await portfolioAPI.getMyPortfolios();
      setPortfolios(response.portfolios);
      setError('');
    } catch (error: any) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await portfolioAPI.getMyPortfolioStats();
      setStats(response);
    } catch (error: any) {
      console.error('Failed to load stats:', error);
    }
  };
  const openDeleteModal = (portfolio: Portfolio) => {
    setPortfolioToDelete(portfolio);
    setShowDeleteModal(true);
  };
  const handleDeletePortfolio = async () => {
    if (!portfolioToDelete) return;

    try {
      setIsDeletingPortfolio(true);
      await portfolioAPI.deletePortfolio(portfolioToDelete.id);
      setPortfolios(prev => prev.filter(p => p.id !== portfolioToDelete.id));
      loadStats(); 
      setShowDeleteModal(false);
      setPortfolioToDelete(null);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setIsDeletingPortfolio(false);
    }
  };

  const togglePublicStatus = async (portfolio: Portfolio) => {
    try {
      const updatedData = {
        ...portfolio,
        is_public: !portfolio.is_public
      };
      
      await portfolioAPI.updatePortfolio(portfolio.id, updatedData);
      
      setPortfolios(prev => 
        prev.map(p => 
          p.id === portfolio.id 
            ? { ...p, is_public: !p.is_public }
            : p
        )
      );
    } catch (error: any) {
      setError(error.message);
    }
  };

  const createNewPortfolio = async () => {
    try {
      const newPortfolio = {
        title: `Новый проект ${portfolios.length + 1}`,
        description: 'Описание проекта',
        html_content: '<!DOCTYPE html>\n<html>\n<head>\n    <title>Мой проект</title>\n</head>\n<body>\n    <h1>Привет, мир!</h1>\n</body>\n</html>',
        css_content: 'body {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n    background-color: #f0f0f0;\n}\n\nh1 {\n    color: #333;\n    text-align: center;\n}',
        js_content: 'console.log("Привет из JavaScript!");',
        tags: ['html', 'css', 'javascript']
      };

      const response = await portfolioAPI.createPortfolio(newPortfolio);
      
      router.push(`/portfolio/edit/me?project=${response.id}`);
    } catch (error: any) {
      setError(error.message);
    }
  };

  const getFilteredPortfolios = () => {
    if (selectedCategory === 'all') {
      return portfolios;
    }
    return portfolios.filter(portfolio => 
      portfolio.tags.some(tag => 
        tag.toLowerCase().includes(selectedCategory.toLowerCase())
      )
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const PortfolioCard = ({ portfolio }: { portfolio: Portfolio }) => {
    const [previewUrl, setPreviewUrl] = useState<string>('');

    useEffect(() => {
      // Создаем превью на основе HTML/CSS/JS контента
      const createPreview = () => {
        const fullHTML = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${portfolio.title}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: hidden; /* Убираем скролл для превью */
        }
        ${portfolio.css_content || ''}
    </style>
</head>
<body>
    ${portfolio.html_content || ''}
    <script>
        // Изолируем JS код для превью
        (function() {
            'use strict';
            try {
                ${portfolio.js_content || ''}
            } catch(error) {
                console.warn('Portfolio preview JS error:', error.message);
            }
        })();
    </script>
</body>
</html>`;

        try {
          const blob = new Blob([fullHTML], { type: 'text/html; charset=utf-8' });
          const url = URL.createObjectURL(blob);
          setPreviewUrl(url);

          // Очистка предыдущего URL
          return () => {
            URL.revokeObjectURL(url);
          };
        } catch (error) {
          console.error('Preview creation error:', error);
        }
      };

      const cleanup = createPreview();
      return cleanup;
    }, [portfolio.html_content, portfolio.css_content, portfolio.js_content, portfolio.title]);

    const openFullPreview = () => {
      if (previewUrl) {
        window.open(previewUrl, '_blank');
      }
    };

    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden hover:border-gray-700 transition-all duration-200 group">
        {/* Preview */}
        <div className="h-48 bg-gray-800 relative overflow-hidden">
          {previewUrl ? (
            <iframe
              src={previewUrl}
              className="w-full h-full transform scale-75 origin-top-left pointer-events-none"
              title={`Preview of ${portfolio.title}`}
              sandbox="allow-scripts allow-same-origin"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-800">
              <div className="text-center">
                <div className="text-4xl mb-2">📝</div>
                <div className="text-gray-400 text-sm">Загрузка превью...</div>
              </div>
            </div>
          )}
          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <div className="flex space-x-2">
              <button
                onClick={openFullPreview}
                className="bg-white text-black px-3 py-2 rounded font-medium hover:bg-gray-100 transition-colors"
              >
                Открыть
              </button>
              <button
                onClick={() => router.push(`/portfolio/edit/me?project=${portfolio.id}`)}
                className="bg-gray-800 text-white px-3 py-2 rounded font-medium hover:bg-gray-700 transition-colors"
              >
                Редактировать
              </button>
            </div>
          </div>
        </div>
      
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors mb-1">
              {portfolio.title}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                </svg>
                {portfolio.views}
              </span>
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                </svg>
                {portfolio.likes}
              </span>
              <span className={`px-2 py-1 rounded text-xs ${portfolio.is_public ? 'bg-green-900 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                {portfolio.is_public ? 'Публичный' : 'Приватный'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => togglePublicStatus(portfolio)}
              className="text-gray-400 hover:text-white transition-colors p-1"
              title={portfolio.is_public ? 'Сделать приватным' : 'Сделать публичным'}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                {portfolio.is_public ? (
                  <path d="M10 2L3 9h4v6h6v-6h4l-7-7z" />
                ) : (
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                )}
              </svg>
            </button>
            
            <button
              onClick={() => openDeleteModal(portfolio)}
              className="text-gray-400 hover:text-red-400 transition-colors p-1"
              title="Удалить проект"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
        
        <p className="text-gray-400 mb-4 text-sm overflow-hidden" style={{
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical'
        }}>{portfolio.description}</p>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {portfolio.tags.map((tag, index) => (
            <span 
              key={index}
              className="bg-gray-800 text-gray-300 px-2 py-1 rounded text-xs hover:bg-gray-700 transition-colors cursor-pointer"
              onClick={() => setSelectedCategory(tag)}
            >
              {tag}
            </span>
          ))}
        </div>
        
        <div className="text-sm text-gray-400">
          Обновлено {formatDate(portfolio.updated_at)}
        </div>
      </div>
    </div>
    );
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-center py-16">
          <div className="text-white">Загрузка портфолио...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header with Stats */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Портфолио</h1>
          <p className="text-gray-400">Ваши проекты и работы</p>
          <div className="flex items-center space-x-6 mt-3 text-sm">
            <span className="text-gray-300">
              <strong>{stats.portfolios_count}</strong> из 5 проектов
            </span>
            <span className="text-gray-300">
              <strong>{stats.total_views}</strong> просмотров
            </span>
            <span className="text-gray-300">
              <strong>{stats.total_likes}</strong> лайков
            </span>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={() => createNewPortfolio()}
            className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            disabled={stats.remaining_slots === 0}
          >
            {stats.remaining_slots > 0 ? 'Создать портфолио' : 'Лимит достигнут'}
          </button>
          <button
            onClick={() => router.push('/portfolio/edit/me')}
            className="bg-gray-800 border border-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Редактор
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Categories */}
      <div className="flex items-center space-x-4 mb-8 overflow-x-auto">
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
            selectedCategory === 'all'
              ? 'bg-white text-black'
              : 'bg-gray-800 border border-gray-700 text-white hover:bg-gray-700'
          }`}
        >
          Все ({portfolios.length})
        </button>
        {['html', 'css', 'javascript', 'react', 'vue', 'angular'].map(category => {
          const count = portfolios.filter(p => 
            p.tags.some(tag => tag.toLowerCase().includes(category.toLowerCase()))
          ).length;
          
          if (count === 0) return null;
          
          return (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? 'bg-white text-black'
                  : 'bg-gray-800 border border-gray-700 text-white hover:bg-gray-700'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)} ({count})
            </button>
          );
        })}
      </div>

      {/* Portfolio Grid */}
      {getFilteredPortfolios().length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {getFilteredPortfolios().map((portfolio) => (
            <PortfolioCard key={portfolio.id} portfolio={portfolio} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <svg className="w-24 h-24 mx-auto text-gray-600 mb-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
          <h3 className="text-xl font-bold text-white mb-2">
            {selectedCategory === 'all' ? 'Портфолио пустое' : 'Нет проектов в этой категории'}
          </h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            {selectedCategory === 'all' 
              ? 'Создайте свой первый проект в нашем редакторе. Покажите свои навыки в HTML, CSS и JavaScript!'
              : `Нет проектов с тегом "${selectedCategory}". Создайте новый проект или измените фильтр.`
            }
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => createNewPortfolio()}
              className="bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              disabled={stats.remaining_slots === 0}
            >
              {selectedCategory === 'all' ? 'Создать первое портфолио' : 'Создать портфолио'}
            </button>
            {selectedCategory !== 'all' && (
              <button
                onClick={() => setSelectedCategory('all')}
                className="bg-gray-800 border border-gray-700 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Показать все
              </button>
            )}
          </div>
        </div>
      )}

      {/* Модальное окно удаления */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeletePortfolio}
        title="Удалить проект портфолио"
        message={`Вы уверены, что хотите удалить проект "${portfolioToDelete?.title}"? Это действие необратимо и все файлы будут удалены с сервера.`}
        confirmText="Удалить"
        cancelText="Отмена"
        type="danger"
        isLoading={isDeletingPortfolio}
      />
    </div>
  );
} 