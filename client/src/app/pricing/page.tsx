'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../../components/ui/dashboard-layout';
import { 
  HiCheck, 
  HiX, 
  HiStar, 
  HiSparkles, 
  HiCube, 
  HiGlobeAlt,
  HiChartBar,
  HiCloud,
  HiShieldCheck,
  HiCog,
  HiUserGroup,
  HiDocumentText,
  HiCode,
  HiDatabase,
  HiServer,
  HiLightningBolt,
  HiLockClosed,
  HiEye,
  HiDownload
} from 'react-icons/hi';
import './pricing.scss';

interface PricingPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  priceCrypto: string;
  period: string;
  features: {
    text: string;
    included: boolean;
    premium?: boolean;
    pro?: boolean;
  }[];
  popular?: boolean;
  recommended?: boolean;
}

const pricingPlans: PricingPlan[] = [
  {
    id: 'free',
    name: 'Free',
    description: 'Для начинающих разработчиков',
    price: 0,
    priceCrypto: '0 BTC',
    period: 'навсегда',
    features: [
      { text: '3 портфолио', included: true },
      { text: '100MB хранилище', included: true },
      { text: 'Базовые шаблоны', included: true },
      { text: 'Email поддержка', included: true },
      { text: 'AI генерация', included: false },
      { text: 'Кастомные домены', included: false },
      { text: 'Продвинутая аналитика', included: false },
      { text: 'API доступ', included: false },
      { text: 'Приоритетная поддержка', included: false },
      { text: 'Неограниченное хранилище', included: false },
      { text: 'Команды и группы', included: false },
      { text: 'Экспорт в PDF', included: false },
    ]
  },
  {
    id: 'premium',
    name: 'Premium',
    description: 'Для профессионалов',
    price: 9.99,
    priceCrypto: '0.0004 BTC',
    period: 'в месяц',
    popular: true,
    recommended: true,
    features: [
      { text: 'Неограниченные портфолио', included: true },
      { text: '5GB хранилище', included: true },
      { text: 'AI генерация (10/день)', included: true },
      { text: 'Премиум шаблоны', included: true },
      { text: 'Приоритетная поддержка', included: true },
      { text: 'Продвинутая аналитика', included: true },
      { text: 'Кастомные домены', included: true },
      { text: 'Экспорт в PDF', included: true },
      { text: 'API доступ', included: false },
      { text: 'Неограниченное хранилище', included: false },
      { text: 'Команды и группы', included: false },
      { text: 'Прямая поддержка', included: false },
    ]
  },
  {
    id: 'pro',
    name: 'Pro',
    description: 'Для команд и агентств',
    price: 19.99,
    priceCrypto: '0.0008 BTC',
    period: 'в месяц',
    features: [
      { text: 'Все из Premium', included: true },
      { text: 'AI генерация (50/день)', included: true },
      { text: 'Неограниченное хранилище', included: true },
      { text: 'API доступ', included: true },
      { text: 'Команды и группы', included: true },
      { text: 'Прямая поддержка', included: true },
      { text: 'GitHub интеграция', included: true },
      { text: 'Множественные домены', included: true },
      { text: 'Экспорт данных', included: true },
      { text: 'Приоритетная обработка', included: true },
      { text: 'Кастомные интеграции', included: true },
      { text: 'Белый лейбл', included: true },
    ]
  }
];

export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const getDiscountedPrice = (price: number) => {
    if (billingPeriod === 'yearly') {
      return price * 0.8; // 20% скидка за год
    }
    return price;
  };

  const handlePlanSelect = (planId: string) => {
    setSelectedPlan(planId);
    // Здесь будет логика для перехода к оплате
    console.log('Selected plan:', planId);
  };

  return (
    <DashboardLayout activePage="pricing">
    <div className="pricing-page">
      {/* Background Effects */}
      <div className="pricing-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      {/* Header */}
      <motion.div 
        className="pricing-header"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.5 }}
      >
        <div className="container">
          <div className="header-content">
            <motion.div 
              className="badge"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.8, type: "spring" }}
            >
              <HiSparkles />
              <span>Премиум функции</span>
            </motion.div>
            
            <motion.h1 
              className="title"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              Выберите свой план
            </motion.h1>
            
            <motion.p 
              className="subtitle"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0 }}
            >
              Начните бесплатно и масштабируйтесь по мере роста
            </motion.p>

            {/* Billing Toggle */}
            <motion.div 
              className="billing-toggle"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.1 }}
            >
              <span className={billingPeriod === 'monthly' ? 'active' : ''}>Ежемесячно</span>
              <button 
                className={`toggle-button ${billingPeriod === 'yearly' ? 'active' : ''}`}
                onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'yearly' : 'monthly')}
              >
                <div className="toggle-slider"></div>
              </button>
              <span className={billingPeriod === 'yearly' ? 'active' : ''}>
                Ежегодно
                <span className="discount-badge">-20%</span>
              </span>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Pricing Cards */}
      <div className="pricing-cards">
        <div className="container">
          <div className="cards-grid">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={plan.id}
                className={`pricing-card ${plan.popular ? 'popular' : ''} ${plan.recommended ? 'recommended' : ''}`}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1, duration: 0.6 }}
                whileHover={{ y: -10, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {plan.popular && (
                  <div className="popular-badge">
                    <HiStar />
                    <span>Рекомендуемый</span>
                  </div>
                )}

                <div className="card-header">
                  <div className="plan-icon">
                    {plan.id === 'free' && <HiCube />}
                    {plan.id === 'premium' && <HiSparkles />}
                    {plan.id === 'pro' && <HiLightningBolt />}
                  </div>
                  
                  <h3 className="plan-name">{plan.name}</h3>
                  <p className="plan-description">{plan.description}</p>
                  
                  <div className="price-section">
                    <div className="price">
                      <span className="currency">$</span>
                      <span className="amount">{getDiscountedPrice(plan.price)}</span>
                      <span className="period">/{billingPeriod === 'monthly' ? 'мес' : 'год'}</span>
                    </div>
                    <div className="crypto-price">
                      {plan.priceCrypto}
                    </div>
                  </div>
                </div>

                <div className="card-features">
                  <ul className="features-list">
                    {plan.features.map((feature, featureIndex) => (
                      <motion.li
                        key={featureIndex}
                        className={`feature-item ${feature.included ? 'included' : 'excluded'}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 + featureIndex * 0.05 }}
                      >
                        <div className="feature-icon">
                          {feature.included ? (
                            <HiCheck className="check-icon" />
                          ) : (
                            <HiX className="x-icon" />
                          )}
                        </div>
                        <span className="feature-text">{feature.text}</span>
                      </motion.li>
                    ))}
                  </ul>
                </div>

                <div className="card-actions">
                  <motion.button
                    className={`select-plan-btn ${plan.id === 'free' ? 'free' : 'premium'}`}
                    onClick={() => handlePlanSelect(plan.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {plan.id === 'free' ? 'Начать бесплатно' : 'Выбрать план'}
                  </motion.button>
                  
                  {plan.id !== 'free' && (
                    <p className="trial-text">
                      7 дней бесплатно • Отмена в любое время
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Comparison */}
      <motion.div 
        className="features-comparison"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <div className="container">
          <h2 className="section-title">Сравнение функций</h2>
          
          <div className="comparison-table">
            <div className="table-header">
              <div className="feature-name">Функция</div>
              <div className="plan-column">Free</div>
              <div className="plan-column popular">Premium</div>
              <div className="plan-column">Pro</div>
            </div>
            
            <div className="table-body">
              <div className="table-row">
                <div className="feature-name">Портфолио</div>
                <div className="plan-value">3</div>
                <div className="plan-value popular">∞</div>
                <div className="plan-value">∞</div>
              </div>
              
              <div className="table-row">
                <div className="feature-name">Хранилище</div>
                <div className="plan-value">100MB</div>
                <div className="plan-value popular">5GB</div>
                <div className="plan-value">∞</div>
              </div>
              
              <div className="table-row">
                <div className="feature-name">AI генерации</div>
                <div className="plan-value">0</div>
                <div className="plan-value popular">10/день</div>
                <div className="plan-value">50/день</div>
              </div>
              
              <div className="table-row">
                <div className="feature-name">Кастомные домены</div>
                <div className="plan-value" style={{display:'flex',justifyContent:'center',alignItems:'center'}}><HiX className="x-icon" /></div>
                <div className="plan-value popular" style={{display:'flex',justifyContent:'center',alignItems:'center'}}><HiCheck className="check-icon" /></div>
                <div className="plan-value" style={{display:'flex',justifyContent:'center',alignItems:'center'}}><HiCheck className="check-icon" /></div>
              </div>
              
              <div className="table-row">
                <div className="feature-name">API доступ</div>
                <div className="plan-value" style={{display:'flex',justifyContent:'center',alignItems:'center'}}><HiX className="x-icon" /></div>
                <div className="plan-value popular" style={{display:'flex',justifyContent:'center',alignItems:'center'}}><HiX className="x-icon" /></div>
                <div className="plan-value" style={{display:'flex',justifyContent:'center',alignItems:'center'}}><HiCheck className="check-icon" /></div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* FAQ Section */}
      <motion.div 
        className="faq-section"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
      >
        <div className="container">
          <h2 className="section-title">Часто задаваемые вопросы</h2>
          
          <div className="faq-grid">
            <div className="faq-item">
              <h3>Могу ли я отменить подписку?</h3>
              <p>Да, вы можете отменить подписку в любое время. Доступ к функциям сохранится до конца оплаченного периода.</p>
            </div>
            
            <div className="faq-item">
              <h3>Есть ли пробный период?</h3>
              <p>Да, все платные планы включают 7-дневный бесплатный пробный период. Никаких обязательств.</p>
            </div>
            
            <div className="faq-item">
              <h3>Какие способы оплаты?</h3>
              <p>Мы принимаем все основные криптовалюты через CryptoCloud: Bitcoin, Ethereum, USDT и другие.</p>
            </div>
            
            <div className="faq-item">
              <h3>Что происходит с данными при отмене?</h3>
              <p>Ваши данные сохраняются 30 дней после отмены. Вы можете восстановить доступ, возобновив подписку.</p>
            </div>
          </div>
        </div>
      </motion.div>

    </div>
    </DashboardLayout>
  );
} 