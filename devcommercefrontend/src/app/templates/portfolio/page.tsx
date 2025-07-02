'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { templatesAPI, TEMPLATE_DIFFICULTIES, TEMPLATE_SORT_OPTIONS, getTemplateErrorMessage } from '../../../api/templates/api';
import { useAuth } from '../../../contexts/AuthContext';
import UseTemplateModal from './components/usetemplate/usetemplate';
import DashboardLayout from '../../../components/ui/dashboard-layout';
import { 
  HiOutlineEye, 
  HiOutlineFire, 
  HiOutlineUser, 
  HiOutlineChartBar,
  HiOutlineTemplate,
  HiOutlineGlobeAlt,
  HiOutlineColorSwatch,
  HiOutlineCog,
  HiOutlineDeviceMobile,
  HiOutlineCloud,
  HiOutlineChartPie,
  HiOutlineBeaker,
  HiOutlineShieldCheck,
  HiOutlineCube,
  HiOutlinePuzzle,
  HiOutlineLightBulb,
  HiOutlineCloudUpload,
  HiOutlineDocumentText,
  HiOutlinePresentationChartLine,
  HiOutlineUsers,
  HiOutlinePencil,
  HiOutlineBriefcase
} from "react-icons/hi";
import './style.scss';
interface Template {
  id: number;
  title: string;
  description: string;
  category: string;
  category_display: string;
  difficulty: string;
  difficulty_display: string;
  thumbnail_image?: string;
  demo_url?: string;
  likes: number;
  views: number;
  uses: number;
  is_featured: boolean;
  is_premium: boolean;
  created_by_username: string;
  created_at: string;
  tags: string[];
  is_liked_by_user: boolean;
}

interface Category {
  code: string;
  display: string;
  count: number;
}

export default function TemplatesPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    difficulty: '',
    is_premium: undefined as boolean | undefined,
    featured: false,
    search: '',
    sort: 'featured'
  });
  
  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    totalCount: 0
  });
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [showUseTemplateModal, setShowUseTemplateModal] = useState(false);
  const [isUsingTemplate, setIsUsingTemplate] = useState(false);
  useEffect(() => {
    loadTemplates();
  }, [filters, pagination.page]);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadTemplates = async () => {
    try {
      setIsLoading(true);
      const params = {
        ...filters,
        page: pagination.page,
        page_size: 12
      };
      
      const response = await templatesAPI.getTemplates(params);
      if (response && (response.results || Array.isArray(response))) {
        const templatesList = response.results || response;
        setTemplates(templatesList);
        if (response.count !== undefined) {
          setPagination(prev => ({
            ...prev,
            totalCount: response.count || 0,
            totalPages: Math.ceil((response.count || 0) / 12)
          }));
        }
      } else {
        setTemplates([]);
      }
    } catch (error: any) {
      setError('Ошибка подключения к серверу');
      console.error('Ошибка загрузки шаблонов:', error);
      setTemplates([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await templatesAPI.getCategories();
      if (response && Array.isArray(response)) {
        setCategories(response);
      } else if (response && response.results && Array.isArray(response.results)) {
        setCategories(response.results);
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
    }
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSearch = (searchValue: string) => {
    setFilters(prev => ({
      ...prev,
      search: searchValue
    }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleLikeTemplate = async (templateId: number) => {
    if (!user) {
      router.push('/auth');
      return;
    }

    try {
      const template = templates.find(t => t.id === templateId);
      if (!template) return;

      if (template.is_liked_by_user) {
        await templatesAPI.unlikeTemplate(templateId);
      } else {
        await templatesAPI.likeTemplate(templateId);
      }
      setTemplates(prev => prev.map(t => 
        t.id === templateId 
          ? {
              ...t,
              is_liked_by_user: !t.is_liked_by_user,
              likes: t.is_liked_by_user ? t.likes - 1 : t.likes + 1
            }
          : t
      ));
    } catch (error: any) {
      console.error('Ошибка лайка:', error);
    }
  };

  const handleUseTemplate = (template: Template) => {
    if (!user) {
      router.push('/auth');
      return;
    }

    setSelectedTemplate(template);
    setShowUseTemplateModal(true);
  };

  const handleConfirmUseTemplate = async (projectData: { title: string; description: string }) => {
    if (!selectedTemplate) return;

    try {
      setIsUsingTemplate(true);
      const response = await templatesAPI.useTemplate(selectedTemplate.id, projectData);
      
      if (response && (response.portfolio || response.edit_url)) {
        const editUrl = response.edit_url || response.portfolio?.edit_url || '/portfolio/edit/me';
        setShowUseTemplateModal(false);
        router.push(editUrl);
      }
    } catch (error: any) {
      if (error.code === 'PREMIUM_REQUIRED') {
        setError('Этот шаблон доступен только Premium пользователям');
      } else {
        setError(getTemplateErrorMessage(error));
      }
    } finally {
      setIsUsingTemplate(false);
    }
  };

  const handleCloseUseTemplateModal = () => {
    if (!isUsingTemplate) {
      setShowUseTemplateModal(false);
      setSelectedTemplate(null);
    }
  };

  const openPreview = (template: Template) => {
    setSelectedTemplate(template);
    setShowPreviewModal(true);
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: React.ReactElement } = {
      'fullstack': <HiOutlineGlobeAlt />,
      'frontend': <HiOutlineColorSwatch />,
      'backend': <HiOutlineCog />,
      'mobile': <HiOutlineDeviceMobile />,
      'devops': <HiOutlineCloud />,
      'data_scientist': <HiOutlineChartPie />,
      'ml_engineer': <HiOutlineLightBulb />,
      'qa_engineer': <HiOutlineBeaker />,
      'ui_designer': <HiOutlineColorSwatch />,
      'product_manager': <HiOutlinePresentationChartLine />,
      'cyber_security': <HiOutlineShieldCheck />,
      'blockchain': <HiOutlineCube />,
      'game_developer': <HiOutlinePuzzle />,
      'ai_engineer': <HiOutlineLightBulb />,
      'cloud_architect': <HiOutlineCloudUpload />,
      'business_analyst': <HiOutlinePresentationChartLine />,
      'scrum_master': <HiOutlineUsers />,
      'technical_writer': <HiOutlineDocumentText />,
      'sales_engineer': <HiOutlineBriefcase />,
      'other': <HiOutlineCog />
    };
    return icons[category] || <HiOutlineCog />;
  };

  return (
    <DashboardLayout activePage="templates">
      <div className="templates-page">
      <section className="templates-hero">
        <div className="templates-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Шаблоны портфолио
              <span className="gradient-text"> для IT специалистов</span>
            </h1>
            <p className="hero-subtitle">
              Готовые профессиональные шаблоны для быстрого создания впечатляющего портфолио. 
              Выберите подходящий дизайн и адаптируйте под свои потребности.
            </p>
            <div className="hero-search">
              <div className="search-input-wrapper">
                <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.35-4.35"></path>
                </svg>
                <input
                  type="text"
                  placeholder="Поиск шаблонов..."
                  value={filters.search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="search-input"
                />
              </div>
            </div>
          </div>
        </div>
      </section>
      <section className="templates-filters">
        <div className="templates-container">
          <div className="filters-grid">
            <div className="filter-group">
              <label className="filter-label">Специализация</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="filter-select"
              >
                <option value="">Все специализации</option>
                {categories.map(category => (
                  <option key={category.code} value={category.code}>
                    {getCategoryIcon(category.code)} {category.display} ({category.count})
                  </option>
                ))}
              </select>
            </div>

            {/* Difficulty Filter */}
            <div className="filter-group">
              <label className="filter-label">Сложность</label>
              <select
                value={filters.difficulty}
                onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                className="filter-select"
              >
                <option value="">Любая сложность</option>
                {Object.entries(TEMPLATE_DIFFICULTIES).map(([key, value]) => (
                  <option key={key} value={key}>{value}</option>
                ))}
              </select>
            </div>

            {/* Sort Filter */}
            <div className="filter-group">
              <label className="filter-label">Сортировка</label>
              <select
                value={filters.sort}
                onChange={(e) => handleFilterChange('sort', e.target.value)}
                className="filter-select"
              >
                {Object.entries(TEMPLATE_SORT_OPTIONS).map(([key, value]) => (
                  <option key={key} value={key}>{value}</option>
                ))}
              </select>
            </div>

            {/* Premium Filter */}
            <div className="filter-group">
              <div className="filter-checkboxes">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.featured}
                    onChange={(e) => handleFilterChange('featured', e.target.checked)}
                  />
                  <span className="checkbox-text">Только рекомендуемые</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Error Message */}
      {error && (
        <div className="templates-container">
          <div className="error-message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            {error}
            <button onClick={() => setError('')} className="error-close">×</button>
          </div>
        </div>
      )}

      {/* Templates Grid */}
      <section className="templates-grid-section">
        <div className="templates-container">
          {isLoading ? (
            <div className="loading-grid">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="template-card-skeleton">
                  <div className="skeleton-image"></div>
                  <div className="skeleton-content">
                    <div className="skeleton-title"></div>
                    <div className="skeleton-description"></div>
                    <div className="skeleton-tags"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : templates.length > 0 ? (
            <>
              <div className="templates-grid">
                {templates.map((template) => (
                  <div key={template.id} className="template-card">
                    {/* Template Preview */}
                    <div className="template-preview" onClick={() => openPreview(template)}>
                      {template.demo_url ? (
                        <iframe
                          src={template.demo_url}
                          className="preview-iframe-card"
                          title={`Превью ${template.title}`}
                          loading="lazy"
                        />
                      ) : template.thumbnail_image ? (
                        <img 
                          src={template.thumbnail_image} 
                          alt={template.title}
                          className="preview-image"
                        />
                      ) : (
                        <div className="preview-placeholder">
                          <div className="placeholder-icon">
                            {getCategoryIcon(template.category)}
                          </div>
                          <div className="placeholder-text">Превью</div>
                        </div>
                      )}
                      
                      {/* Overlay */}
                      <div className="preview-overlay">
                        <button className="preview-button">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                          {template.demo_url ? 'Увеличить' : 'Предпросмотр'}
                        </button>
                      </div>

                      {/* Badges */}
                      <div className="template-badges">
                        {template.is_featured && (
                          <span className="badge badge-featured">
                            <HiOutlineFire /> Топ
                          </span>
                        )}
                        {template.is_premium && (
                          <span className="badge badge-premium">
                            <HiOutlineCube /> Premium
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Template Info */}
                    <div className="template-info">
                      <div className="template-header">
                        <h3 className="template-title">{template.title}</h3>
                        <button
                          onClick={() => handleLikeTemplate(template.id)}
                          className={`like-button ${template.is_liked_by_user ? 'liked' : ''}`}
                        >
                          <svg viewBox="0 0 24 24" fill={template.is_liked_by_user ? 'currentColor' : 'none'} stroke="currentColor">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                          </svg>
                          {template.likes}
                        </button>
                      </div>

                      <p className="template-description">{template.description}</p>

                      {/* Template Meta */}
                      <div className="template-meta">
                        <div className="meta-item">
                          <span className="meta-icon">{getCategoryIcon(template.category)}</span>
                          <span className="meta-text">{template.category_display}</span>
                        </div>
                        <div className="meta-item">
                          <span className="meta-icon"><HiOutlineChartBar /></span>
                          <span className="meta-text">{template.difficulty_display}</span>
                        </div>
                      </div>

                      {/* Template Stats */}
                                              <div className="template-stats">
                          <div className="stat">
                            <span className="stat-icon"><HiOutlineEye /></span>
                            <span className="stat-value">{template.views}</span>
                          </div>
                          <div className="stat">
                            <span className="stat-icon"><HiOutlineFire /></span>
                            <span className="stat-value">{template.uses}</span>
                          </div>
                          <div className="stat">
                            <span className="stat-icon"><HiOutlineUser /></span>
                            <span className="stat-value">{template.created_by_username}</span>
                          </div>
                        </div>

                      {/* Template Tags */}
                      {template.tags && template.tags.length > 0 && (
                        <div className="template-tags">
                          {template.tags.slice(0, 3).map((tag, index) => (
                            <span key={index} className="tag">
                              {tag}
                            </span>
                          ))}
                          {template.tags.length > 3 && (
                            <span className="tag-more">+{template.tags.length - 3}</span>
                          )}
                        </div>
                      )}

                      {/* Action Button */}
                      <button
                        onClick={() => handleUseTemplate(template)}
                        disabled={isUsingTemplate}
                        className="use-template-button"
                      >
                        {isUsingTemplate ? (
                          <>
                            <div className="button-spinner"></div>
                            Создаем...
                          </>
                        ) : (
                          <>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                              <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
                              <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
                              <path d="M2 2l7.586 7.586"></path>
                              <circle cx="11" cy="11" r="2"></circle>
                            </svg>
                            Использовать шаблон
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {pagination.totalPages > 1 && (
                <div className="pagination">
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="pagination-button"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <polyline points="15,18 9,12 15,6"></polyline>
                    </svg>
                    Назад
                  </button>
                  
                  <div className="pagination-info">
                    Страница {pagination.page} из {pagination.totalPages}
                  </div>
                  
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                    disabled={pagination.page === pagination.totalPages}
                    className="pagination-button"
                  >
                    Далее
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <polyline points="9,18 15,12 9,6"></polyline>
                    </svg>
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon"><HiOutlineTemplate /></div>
              <h3 className="empty-title">Шаблоны не найдены</h3>
              <p className="empty-description">
                Попробуйте изменить фильтры или поисковый запрос
              </p>
              <button 
                onClick={() => {
                  setFilters({
                    category: '',
                    difficulty: '',
                    is_premium: undefined,
                    featured: false,
                    search: '',
                    sort: 'featured'
                  });
                  setPagination(prev => ({ ...prev, page: 1 }));
                }}
                className="reset-filters-button"
              >
                Сбросить фильтры
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Preview Modal */}
      {showPreviewModal && selectedTemplate && (
        <div className="modal-overlay" onClick={() => setShowPreviewModal(false)}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{selectedTemplate.title}</h2>
              <button 
                onClick={() => setShowPreviewModal(false)}
                className="modal-close"
              >
                ×
              </button>
            </div>
            <div className="modal-content">
              <iframe
                src={selectedTemplate.demo_url}
                className="preview-iframe"
                title={`Превью ${selectedTemplate.title}`}
              />
            </div>
            <div className="modal-footer">
              <button
                onClick={() => setShowPreviewModal(false)}
                className="modal-button secondary"
              >
                Закрыть
              </button>
              <button
                onClick={() => {
                  setShowPreviewModal(false);
                  handleUseTemplate(selectedTemplate);
                }}
                className="modal-button primary"
              >
                Использовать шаблон
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Use Template Modal */}
      <UseTemplateModal
        isOpen={showUseTemplateModal}
        onClose={handleCloseUseTemplateModal}
        template={selectedTemplate}
        onConfirm={handleConfirmUseTemplate}
        isLoading={isUsingTemplate}
      />
      </div>
    </DashboardLayout>
  );
} 