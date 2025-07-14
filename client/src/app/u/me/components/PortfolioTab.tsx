'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../../contexts/AuthContext';
import { portfolioAPI } from '../../../../api/portfolio/api';
import ConfirmModal from '../../../../components/ui/confirm-modal';
import SimpleLoader from '@/components/simple-loader';  
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
  const { user } = useAuth();
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
  const [copySuccess, setCopySuccess] = useState<string | null>(null);
  const [showCreateDropdown, setShowCreateDropdown] = useState(false);
  
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadPortfolios();
    loadStats();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowCreateDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
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
      
      router.push(`/portfolio/edit/me?project=${response.portfolio.id}`);
    } catch (error: any) {
      setError(error.message);
    }
  };

  const handleCreateManually = () => {
    setShowCreateDropdown(false);
    createNewPortfolio();
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

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess('Ссылка скопирована!');
      setTimeout(() => setCopySuccess(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      setCopySuccess('Ошибка копирования');
      setTimeout(() => setCopySuccess(null), 2000);
    }
  };

  const PortfolioCard = ({ portfolio }: { portfolio: Portfolio }) => {
    const [previewUrl, setPreviewUrl] = useState<string>('');
    const [isPreviewLoading, setIsPreviewLoading] = useState(true);
    const [previewError, setPreviewError] = useState(false);

    useEffect(() => {
      // Слушатель для сообщений от iframe
      const handleMessage = (event: MessageEvent) => {
        if (event.data === 'preview-loaded') {
          setIsPreviewLoading(false);
        }
      };

      window.addEventListener('message', handleMessage);

      // Создаем превью на основе HTML/CSS/JS контента
      const createPreview = () => {
        setIsPreviewLoading(true);
        setPreviewError(false);
        
        try {
          // Проверяем, есть ли контент для превью
          if (!portfolio.html_content && !portfolio.css_content && !portfolio.js_content) {
            setPreviewError(true);
            setIsPreviewLoading(false);
            return;
          }

          const fullHTML = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${portfolio.title}</title>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        html, body {
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: auto;
            background: #ffffff;
        }
        
        /* Масштабирование для превью */
        body {
            transform: scale(0.7);
            transform-origin: top left;
            width: 142.86%; /* 100% / 0.7 для компенсации масштабирования */
            height: 142.86%;
        }
        
        /* Дополнительные стили для лучшего отображения */
        ${portfolio.css_content || ''}
    </style>
</head>
<body>
    ${portfolio.html_content || '<div style="padding: 20px; text-align: center; color: #666;"><h2>Нет HTML контента</h2><p>Добавьте HTML код для отображения превью</p></div>'}
    <script>
        // Изолируем JS код для превью
        (function() {
            'use strict';
            try {
                // Отключаем потенциально проблематичные API для превью
                if (typeof alert !== 'undefined') {
                    window.alert = function() {};
                }
                if (typeof confirm !== 'undefined') {
                    window.confirm = function() { return false; };
                }
                if (typeof prompt !== 'undefined') {
                    window.prompt = function() { return null; };
                }
                
                ${portfolio.js_content || ''}
            } catch(error) {
                console.warn('Portfolio preview JS error:', error.message);
            }
        })();
        
        // Уведомляем о готовности превью
        window.addEventListener('load', function() {
            try {
                parent.postMessage('preview-loaded', '*');
            } catch(e) {}
        });
    </script>
</body>
</html>`;

          const blob = new Blob([fullHTML], { type: 'text/html; charset=utf-8' });
          const url = URL.createObjectURL(blob);
          setPreviewUrl(url);
          
          // Таймаут для обработки случаев, когда превью не загружается
          setTimeout(() => {
            setIsPreviewLoading(false);
          }, 3000);

          // Очистка предыдущего URL
          return () => {
            URL.revokeObjectURL(url);
          };
        } catch (error) {
          console.error('Preview creation error:', error);
          setPreviewError(true);
          setIsPreviewLoading(false);
        }
      };

      const cleanup = createPreview();
      
      return () => {
        window.removeEventListener('message', handleMessage);
        if (cleanup) cleanup();
      };
    }, [portfolio.html_content, portfolio.css_content, portfolio.js_content, portfolio.title]);

    const openFullPreview = () => {
      // Используем новый публичный URL если портфолио публично
      if (portfolio.is_public && portfolio.public_url) {
        window.open(portfolio.public_url, '_blank');
      } else if (previewUrl) {
        // Fallback на локальное превью для приватных портфолио
        window.open(previewUrl, '_blank');
      }
    };

    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden hover:border-gray-700 transition-all duration-200 group">
        {/* Preview */}
        <div className="h-64 bg-gray-800 relative overflow-hidden rounded-t-lg">
          {previewUrl && !previewError ? (
            <>
              <iframe
                src={previewUrl}
                className="w-full h-full border-none bg-white pointer-events-none"
                title={`Preview of ${portfolio.title}`}
                sandbox="allow-scripts allow-same-origin allow-forms"
                loading="lazy"
                style={{
                  minHeight: '256px',
                  backgroundColor: '#ffffff'
                }}
                onLoad={() => setIsPreviewLoading(false)}
                onError={() => {
                  setPreviewError(true);
                  setIsPreviewLoading(false);
                }}
              />
              {isPreviewLoading && (
                <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
                  <div className="text-center">
                    <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                    <div className="text-gray-400 text-sm">Загрузка превью...</div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-800">
              <div className="text-center">
                {previewError ? (
                  <>
                    <div className="text-4xl mb-2">⚠️</div>
                    <div className="text-gray-400 text-sm mb-1">Ошибка загрузки превью</div>
                    <div className="text-gray-500 text-xs">Проверьте HTML/CSS контент</div>
                  </>
                ) : (
                  <>
                    <div className="text-4xl mb-2">📝</div>
                    <div className="text-gray-400 text-sm">Создание превью...</div>
                  </>
                )}
              </div>
            </div>
          )}
          <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
            <div className="flex space-x-3">
              <button
                onClick={openFullPreview}
                className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors shadow-lg"
              >
                Открыть
              </button>
              <button
                onClick={() => router.push(`/portfolio/edit/me?project=${portfolio.id}`)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-lg"
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
            <div className="flex items-center space-x-4 text-sm text-gray-400 mb-2">
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
            
            {portfolio.is_public && portfolio.public_url && (
              <div className="mb-3 p-3 bg-gray-800 rounded-lg border border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-xs text-gray-400 mb-1">Публичная ссылка:</div>
                    <div className="text-sm font-mono text-blue-400 break-all">
                      {portfolio.public_url}
                    </div>
                  </div>
                  <button
                    onClick={() => copyToClipboard(portfolio.public_url)}
                    className="ml-2 p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                    title="Копировать ссылку"
                  >
                    <svg className="w-4 h-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                      <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
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
      <div className="min-h-screen bg-black flex items-center justify-center">
      <SimpleLoader text="Загрузка портфолио..." fullScreen={true} />
    </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header with Stats */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center space-x-4 mb-2">
            <h1 className="text-2xl font-bold text-white">Портфолио</h1>
          </div>
          <p className="text-gray-400">Ваши проекты и работы</p>
          <div className="flex items-center gap-x-12 mt-3 text-sm">
            <span className="text-gray-300 flex items-center gap-1">
              <strong className="text-white">{stats.portfolios_count}</strong> из 5 проектов
            </span>
            <span className="text-gray-500">•</span>
            <span className="text-gray-300 flex items-center gap-1">
              <strong className="text-white">{stats.total_views}</strong> просмотров
            </span>
            <span className="text-gray-500">•</span>
            <span className="text-gray-300 flex items-center gap-1">
              <strong className="text-white">{stats.total_likes}</strong> лайков
            </span>
          </div>
        </div>
        
        <div className="flex space-x-3">
          {/* Dropdown для создания портфолио */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowCreateDropdown(!showCreateDropdown)}
              className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors flex items-center space-x-2"
              disabled={stats.remaining_slots === 0}
            >
              <span>{stats.remaining_slots > 0 ? 'Создать портфолио' : 'Лимит достигнут'}</span>
              {stats.remaining_slots > 0 && (
                <svg 
                  className={`w-4 h-4 transition-transform ${showCreateDropdown ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              )}
            </button>
            
            {showCreateDropdown && stats.remaining_slots > 0 && (
              <div className="absolute top-full left-0 mt-2 w-64 bg-gray-900 border-2 border-white rounded-lg shadow-lg z-50">
                <div className="p-2">
                  {/* Ручное создание */}
                  <button
                    onClick={handleCreateManually}
                    className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-800 transition-colors text-left"
                  >
                    <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                      <span className="text-white text-lg">📝</span>
                    </div>
                    <div className="flex-1">
                      <div className="text-white font-medium">Создать вручную</div>
                      <div className="text-gray-400 text-sm">Пустой шаблон для редактирования</div>
                    </div>
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateDropdown(false);
                      router.push('/templates/portfolio');
                    }}
                    className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-800 transition-colors text-left relative"
                  >
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <span className="text-white text-lg">🚀</span>
                    </div>
                    <div className="flex-1">
                      <div className="text-white font-medium flex items-center space-x-2">
                        <span>Шаблоны портфолио</span>
                        {!user?.is_premium && <span className="text-yellow-400">🔐</span>}
                      </div>
                      <div className="text-gray-400 text-sm">
                        {user?.is_premium
                          ? 'Посмотрите наши шаблоны портфолио'
                          : 'Доступно только Premium пользователям'
                        }
                      </div>
                    </div>
                    <div className="absolute top-2 right-2">
                      <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">NEW</span>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
          
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
      {copySuccess && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-pulse">
          {copySuccess}
        </div>
      )}
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