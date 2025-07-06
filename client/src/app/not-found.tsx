import Link from 'next/link'
import './404.scss'

export default function NotFound() {
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <div className="grid-overlay"></div>
        <div className="gradient-overlay"></div>
        
        <div className="not-found-main">
          <div className="error-code">
            <span className="error-text">404</span>
          </div>
          
          <div className="error-message">
            <h1>Эта страница не найдена</h1>
            <p>Страница, которую вы ищете, не существует или была перемещена.</p>
          </div>
          
          <div className="error-actions">
            <Link href="/" className="btn-primary">
              Вернуться на главную
            </Link>
            <Link href="/dashboard" className="btn-secondary">
              Перейти к панели управления
            </Link>
          </div>
        </div>
        
        <div className="floating-elements">
          <div className="floating-dot dot-1"></div>
          <div className="floating-dot dot-2"></div>
          <div className="floating-dot dot-3"></div>
          <div className="floating-dot dot-4"></div>
        </div>
      </div>
    </div>
  )
} 