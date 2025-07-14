'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import { portfolioAPI } from '../../../../api/portfolio/api';
import Editor from '@monaco-editor/react';
import ConfirmModal from '../../../../components/ui/confirm-modal';
import CreateProjectModal, { ProjectFormData } from '../../../../components/ui/create-project-modal';
import Loader from '../../../../components/simple-loader';

interface Portfolio {
  id: string;
  title: string;
  description: string;
  html_content: string;
  css_content: string;
  js_content: string;
  is_public: boolean;
  tags: string[];
}

export default function PortfolioEditor() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [currentPortfolio, setCurrentPortfolio] = useState<Portfolio | null>(null);
  const [activeTab, setActiveTab] = useState<'html' | 'css' | 'js'>('html');
  const [isLoadingPortfolios, setIsLoadingPortfolios] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isFullSaving, setIsFullSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isPreviewFullscreen, setIsPreviewFullscreen] = useState(false);
  
  // Состояния модальных окон
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);
  
  const editorRef = useRef<any>(null);
  const previewRef = useRef<HTMLIFrameElement>(null);
  
  const autosaveTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadPortfolios();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (currentPortfolio) {
      updatePreview();
    }
  }, [currentPortfolio?.html_content, currentPortfolio?.css_content, currentPortfolio?.js_content]);
  useEffect(() => {
    const projectId = searchParams.get('project');
    if (projectId && portfolios.length > 0) {
      const targetPortfolio = portfolios.find((p: Portfolio) => p.id === projectId);
      if (targetPortfolio) {
        setCurrentPortfolio(targetPortfolio);
      }
    }
  }, [searchParams, portfolios]);
  // Флаг для отслеживания программных изменений
  const isUpdatingFromCode = useRef(false);
  
  useEffect(() => {
    if (editorRef.current && currentPortfolio && !isUpdatingFromCode.current) {
      const content = getEditorContent();
      const currentValue = editorRef.current.getValue();
      
      // Обновляем только если контент действительно отличается
      if (currentValue !== content) {
        // Сохраняем позицию курсора
        const position = editorRef.current.getPosition();
        
        setTimeout(() => {
          if (editorRef.current && editorRef.current.setValue) {
            try {
              isUpdatingFromCode.current = true;
              editorRef.current.setValue(content);
              
              // Восстанавливаем позицию курсора
              if (position) {
                editorRef.current.setPosition(position);
              }
              
              setTimeout(() => {
                isUpdatingFromCode.current = false;
              }, 100);
            } catch (error) {
              console.warn('Monaco Editor setValue error:', error);
              isUpdatingFromCode.current = false;
            }
          }
        }, 50);
      }
    }
  }, [currentPortfolio, activeTab]);



  const loadPortfolios = async () => {
    try {
      setIsLoadingPortfolios(true);
      const response = await portfolioAPI.getMyPortfolios();
      setPortfolios(response.portfolios);
      if (response.portfolios.length > 0 && !currentPortfolio) {
        setCurrentPortfolio(response.portfolios[0]);
      }
    } catch (error: any) {
      setError(error.message || 'Ошибка загрузки портфолио');
    } finally {
      setIsLoadingPortfolios(false);
    }
  };

  // Открытие модального окна создания проекта
  const openCreateModal = () => {
    setShowCreateModal(true);
  };

  // Создание нового портфолио через модальное окно
  const handleCreateProject = async (projectData: ProjectFormData) => {
    try {
      setIsCreatingProject(true);
      setError('');

      const newPortfolioData = {
        ...projectData,
        html_content: `<div class="container">
    <h1 id="title">Добро пожаловать!</h1>
    <p>Это ваш новый проект портфолио "${projectData.title}".</p>
    <button id="clickBtn">Нажми меня!</button>
</div>`,
        css_content: `/* Стили для проекта "${projectData.title}" */
.container {
    font-family: 'Arial', sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    text-align: center;
}

h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

p {
    font-size: 1.2rem;
    line-height: 1.6;
    margin-bottom: 2rem;
}

button {
    background: white;
    color: #667eea;
    border: none;
    padding: 12px 24px;
    font-size: 1rem;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: bold;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}`,
        js_content: `// JavaScript для проекта "${projectData.title}"

// Ждем загрузки DOM
document.addEventListener("DOMContentLoaded", function() {
    const title = document.getElementById("title");
    const button = document.getElementById("clickBtn");
    
    if (title) {
        title.addEventListener("click", function() {
            title.style.color = title.style.color === "yellow" ? "white" : "yellow";
        });
    }
    
    if (button) {
        button.addEventListener("click", function() {
            alert("Проект '${projectData.title}' работает отлично!");
            button.textContent = "Отлично работает!";
        });
    }
});`,
      };

      const response = await portfolioAPI.createPortfolio(newPortfolioData);
      const newPortfolio = response.portfolio;
      
      setPortfolios(prev => [newPortfolio, ...prev]);
      setCurrentPortfolio(newPortfolio);
      setSuccess(`Проект "${projectData.title}" создан!`);
      setTimeout(() => setSuccess(''), 3000);
      
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set('project', newPortfolio.id);
      window.history.replaceState({}, '', newUrl.toString());
      
      setShowCreateModal(false);
      
    } catch (error: any) {
      setError(error.message || 'Ошибка создания проекта');
      throw error; // Пробрасываем ошибку для обработки в модальном окне
    } finally {
      setIsCreatingProject(false);
    }
  };

  const selectPortfolio = (portfolio: Portfolio) => {
    // Очищаем таймер автосохранения предыдущего проекта
    if (autosaveTimer.current) {
      clearTimeout(autosaveTimer.current);
    }
    
    // Очищаем сообщения об ошибках и успехе
    setError('');
    setSuccess('');
    
    setCurrentPortfolio(portfolio);
    
    // Обновляем URL
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set('project', portfolio.id);
    window.history.replaceState({}, '', newUrl.toString());
    
    // Принудительно обновляем превью после смены проекта
    setTimeout(() => {
      updatePreview();
    }, 100);
  };

  const updateCode = useCallback((newContent: string) => {
    if (!currentPortfolio || isUpdatingFromCode.current) return;

    const fieldName = `${activeTab}_content` as keyof Portfolio;
    
    // Проверяем, действительно ли значение изменилось
    if (currentPortfolio[fieldName] === newContent) return;

    const updatedPortfolio = {
      ...currentPortfolio,
      [fieldName]: newContent
    };
    
    setCurrentPortfolio(updatedPortfolio);
    
    // Обновляем в списке портфолио
    setPortfolios(prev => 
      prev.map(p => p.id === updatedPortfolio.id ? updatedPortfolio : p)
    );
    
    // Сбрасываем таймер автосохранения
    if (autosaveTimer.current) {
      clearTimeout(autosaveTimer.current);
    }
    
    // Устанавливаем новый таймер автосохранения (2 секунды)
    autosaveTimer.current = setTimeout(() => {
      autosaveCode(updatedPortfolio);
    }, 2000); 
  }, [currentPortfolio, activeTab]);

  const autosaveCode = async (portfolio: Portfolio) => {
    if (!portfolio.id) return;

    try {
      setIsSaving(true);
      await portfolioAPI.autosavePortfolio(portfolio.id, {
        html_content: portfolio.html_content,
        css_content: portfolio.css_content,
        js_content: portfolio.js_content
      });
      setLastSaved(new Date());
    } catch (error: any) {
      console.error('Autosave failed:', error);
      setError('Ошибка автосохранения');
    } finally {
      setIsSaving(false);
    }
  };

  const saveAndExit = async () => {
    if (!currentPortfolio) return;

    try {
      setIsFullSaving(true);
      setError('');
      await portfolioAPI.updatePortfolio(currentPortfolio.id, {
        title: currentPortfolio.title,
        description: currentPortfolio.description,
        html_content: currentPortfolio.html_content,
        css_content: currentPortfolio.css_content,
        js_content: currentPortfolio.js_content,
        is_public: currentPortfolio.is_public,
        tags: currentPortfolio.tags
      });
      
      setSuccess('Проект сохранен!');
      setTimeout(() => {
        router.push('/u/me');
      }, 1500);
      
    } catch (error: any) {
      setError(error.message || 'Ошибка сохранения');
    } finally {
      setIsFullSaving(false);
    }
  };

  const updatePreview = useCallback(() => {
    if (!currentPortfolio || !previewRef.current) return;

    const { html_content, css_content, js_content } = currentPortfolio;
    const fullHTML = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Preview</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        ${css_content || ''}
    </style>
</head>
<body>
    ${html_content || ''}
    <script>
        // Изолируем JS код в IIFE для предотвращения конфликтов
        (function() {
            'use strict';
            try {
                ${js_content || ''}
            } catch(error) {
                console.warn('Portfolio JS Error:', error.message);
            }
        })();
    </script>
</body>
</html>`;

    try {
      const blob = new Blob([fullHTML], { type: 'text/html; charset=utf-8' });
      const url = URL.createObjectURL(blob);
      if (previewRef.current.src && previewRef.current.src.startsWith('blob:')) {
        URL.revokeObjectURL(previewRef.current.src);
      }
      
      previewRef.current.src = url;
      setTimeout(() => {
        try {
          URL.revokeObjectURL(url);
        } catch (e) {
        }
      }, 2000);
      
    } catch (error) {
      console.error('Preview update error:', error);
    }
  }, [currentPortfolio]);

  const getEditorContent = () => {
    if (!currentPortfolio) return '';
    
    switch (activeTab) {
      case 'html':
        return currentPortfolio.html_content || '';
      case 'css':
        return currentPortfolio.css_content || '';
      case 'js':
        return currentPortfolio.js_content || '';
      default:
        return '';
    }
  };

  const getLanguage = () => {
    switch (activeTab) {
      case 'html':
        return 'html';
      case 'css':
        return 'css';
      case 'js':
        return 'javascript';
      default:
        return 'html';
    }
  };

  // Открытие модального окна удаления
  const openDeleteModal = () => {
    if (!currentPortfolio) return;
    setShowDeleteModal(true);
  };

  // Удаление портфолио через модальное окно
  const handleDeleteProject = async () => {
    if (!currentPortfolio) return;
    
    try {
      setIsDeletingProject(true);
      await portfolioAPI.deletePortfolio(currentPortfolio.id);
      
      const updatedPortfolios = portfolios.filter(p => p.id !== currentPortfolio.id);
      setPortfolios(updatedPortfolios);
      
      if (updatedPortfolios.length > 0) {
        setCurrentPortfolio(updatedPortfolios[0]);
      } else {
        setCurrentPortfolio(null);
      }
      
      setSuccess(`Проект "${currentPortfolio.title}" удален`);
      setTimeout(() => setSuccess(''), 3000);
      setShowDeleteModal(false);
      
    } catch (error: any) {
      setError(error.message || 'Ошибка удаления проекта');
    } finally {
      setIsDeletingProject(false);
    }
  };

  if (isLoading || isLoadingPortfolios) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
      <Loader text="Загрузка редактора..." fullScreen={true} />
    </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="bg-gray-900 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/u/me')}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← Назад к профилю
            </button>
            <h1 className="text-xl font-bold">Редактор портфолио</h1>
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={currentPortfolio?.id || ''}
              onChange={(e) => {
                const portfolio = portfolios.find((p: Portfolio) => p.id === e.target.value);
                if (portfolio) selectPortfolio(portfolio);
              }}
              className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white min-w-[200px]"
            >
              <option value="">Выберите проект</option>
              {portfolios.map(portfolio => (
                <option key={portfolio.id} value={portfolio.id}>
                  {portfolio.title}
                </option>
              ))}
            </select>
            <button
              onClick={openCreateModal}
              disabled={portfolios.length >= 5}
              className="bg-gray-800 text-white px-3 py-1.5 rounded text-sm hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-gray-600"
            >
              + Новый
            </button>
            {currentPortfolio && (
              <button
                onClick={openDeleteModal}
                className="bg-gray-800 text-white px-3 py-1.5 rounded text-sm hover:bg-gray-700 transition-colors border border-gray-600"
              >
                Удалить
              </button>
            )}
            {currentPortfolio && (
              <button
                onClick={saveAndExit}
                disabled={isFullSaving}
                className="bg-white text-black px-3 py-1.5 rounded text-sm hover:bg-gray-100 disabled:opacity-50 transition-colors"
              >
                {isFullSaving ? 'Сохранение...' : 'Сохранить'}
              </button>
            )}
            <div className="text-sm text-gray-400 min-w-[120px]">
              {isSaving ? (
                <span className="text-yellow-400">⏳ Сохранение...</span>
              ) : lastSaved ? (
                <span className="text-green-400">✅ {lastSaved.toLocaleTimeString()}</span>
              ) : (
                <span className="text-gray-500">Не сохранено</span>
              )}
            </div>
          </div>
        </div>
        {error && (
          <div className="mt-4 bg-red-900/20 border border-red-700 rounded p-3 text-red-400">
            ❌ {error}
          </div>
        )}
        
        {success && (
          <div className="mt-4 bg-green-900/20 border border-green-700 rounded p-3 text-green-400">
            ✅ {success}
          </div>
        )}
        {currentPortfolio && (
          <div className="mt-4 text-sm text-gray-400">
            Проектов: {portfolios.length}/5 • 
            Текущий: {currentPortfolio.title} • 
            Статус: {currentPortfolio.is_public ? 'Публичный' : 'Приватный'}
          </div>
        )}
      </header>

      <div className="flex h-[calc(100vh-120px)]">
        <div className="w-1/2 border-r border-gray-700 flex flex-col">
          <div className="bg-gray-800 border-b border-gray-700 flex">
            {['html', 'css', 'js'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as 'html' | 'css' | 'js')}
                className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors relative ${
                  activeTab === tab
                    ? 'border-blue-500 text-white bg-gray-700'
                    : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                {tab.toUpperCase()}
                {activeTab === tab && (
                  <div className="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>
                )}
              </button>
            ))}
          </div>

          {/* Monaco Editor */}
          <div className="flex-1 bg-gray-900">
            {currentPortfolio ? (
              <Editor
                key={`${currentPortfolio.id}-${activeTab}`}
                height="100%"
                language={getLanguage()}
                value={getEditorContent()}
                onChange={(value) => updateCode(value || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  renderWhitespace: 'selection',
                  tabSize: 2,
                  insertSpaces: true,
                  wordWrap: 'on',
                  automaticLayout: true,
                  scrollBeyondLastLine: false,
                  smoothScrolling: true,
                  cursorBlinking: 'smooth',
                  renderLineHighlight: 'all',
                  bracketPairColorization: {
                    enabled: true
                  }
                }}
                onMount={(editor) => {
                  editorRef.current = editor;
                  if (currentPortfolio) {
                    const content = getEditorContent();
                    isUpdatingFromCode.current = true;
                    editor.setValue(content);
                    setTimeout(() => {
                      isUpdatingFromCode.current = false;
                    }, 100);
                  }
                  
                  editor.focus();
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 flex-col space-y-4">
                <div className="text-6xl">📝</div>
                <div className="text-lg">Выберите или создайте проект для редактирования</div>
                <div className="text-sm text-gray-600">
                  Вы можете создать до 5 проектов портфолио
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Preview */}
        <div className="w-1/2 flex flex-col">
          {/* Preview Header */}
          <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
            <h3 className="font-medium flex items-center space-x-2">
              <span>🔍</span>
              <span>Превью</span>
            </h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsPreviewFullscreen(!isPreviewFullscreen)}
                className="text-gray-400 hover:text-white transition-colors px-2 py-1 rounded"
                title="Полный экран"
              >
                {isPreviewFullscreen ? '🔲' : '⛶'}
              </button>
            </div>
          </div>

          {/* Preview Frame */}
          <div className={`flex-1 ${isPreviewFullscreen ? 'fixed inset-0 z-50 bg-black' : ''}`}>
            {isPreviewFullscreen && (
              <button
                onClick={() => setIsPreviewFullscreen(false)}
                className="absolute top-4 right-4 z-50 bg-black text-white px-3 py-2 rounded"
              >
                ✕ Закрыть
              </button>
            )}
            <iframe
              ref={previewRef}
              className="w-full h-full border-0 bg-white"
              title="Portfolio Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        </div>
      </div>

      {/* Модальные окна */}
      <CreateProjectModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateProject}
        isLoading={isCreatingProject}
        maxProjects={5}
        currentProjectsCount={portfolios.length}
      />

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeleteProject}
        title="Удалить проект"
        message={`Вы уверены, что хотите удалить проект "${currentPortfolio?.title}"? Это действие необратимо.`}
        confirmText="Удалить"
        cancelText="Отмена"
        type="danger"
        isLoading={isDeletingProject}
      />
    </div>
  );
} 