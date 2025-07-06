"use client";
import React from "react";
import Link from "next/link";
import "./style.scss";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-main">
          <div className="footer-brand">
            <div className="footer-logo">
              <Link href="/">
                <span>Dev</span>Commerce
              </Link>
            </div>
            <p className="footer-description">
              Платформа цифровых продуктов для разработчиков
            </p>
            <div className="social-links">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
              </a>
              <a href="https://discord.com" target="_blank" rel="noopener noreferrer" aria-label="Discord">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 0 0-.079.036c-.21.385-.39.774-.53 1.162a16.98 16.98 0 0 0-5.058 0 10.523 10.523 0 0 0-.524-1.162.077.077 0 0 0-.08-.036 18.224 18.224 0 0 0-4.885 1.491.07.07 0 0 0-.032.027C.533 11.046.525 17.407 2.044 19.77c.012.017.028.03.044.033a18.242 18.242 0 0 0 5.52 2.79.08.08 0 0 0 .084-.027c.456-.623.865-1.282 1.213-1.975a.075.075 0 0 0-.041-.106 12.04 12.04 0 0 1-1.71-.817.075.075 0 0 1-.008-.127c.114-.085.228-.175.336-.267a.072.072 0 0 1 .079-.01c3.973 1.815 8.27 1.815 12.198 0a.074.074 0 0 1 .077.011c.11.092.223.18.338.267a.075.075 0 0 1-.006.127c-.544.317-1.115.584-1.712.816a.074.074 0 0 0-.041.107c.357.692.764 1.352 1.212 1.974a.074.074 0 0 0 .084.028c1.961-.607 3.768-1.516 5.522-2.79a.077.077 0 0 0 .044-.034c1.765-2.75 1.52-9.076-.729-13.251a.061.061 0 0 0-.033-.027zM8.023 16.297c-1.093 0-1.995-.997-1.995-2.23 0-1.231.883-2.229 1.995-2.229s2.011.998 1.995 2.23c0 1.232-.882 2.229-1.995 2.229zm7.364 0c-1.093 0-1.994-.997-1.994-2.23 0-1.231.883-2.229 1.994-2.229s2.012.998 1.995 2.23c0 1.232-.882 2.229-1.995 2.229z"/>
                </svg>
              </a>
            </div>
          </div>
          
          <div className="footer-links">
            <div className="footer-links-column">
              <h3>Платформа</h3>
              <ul>
                <li><Link href="/categories">Категории</Link></li>
                <li><Link href="/pricing">Цены</Link></li>
                <li><Link href="/seller/register">Стать продавцом</Link></li>
                <li><Link href="/affiliate">Партнерская программа</Link></li>
              </ul>
            </div>
            
            <div className="footer-links-column">
              <h3>Ресурсы</h3>
              <ul>
                <li><Link href="/blog">Блог</Link></li>
                <li><Link href="/docs">Документация</Link></li>
                <li><Link href="/faqs">FAQ</Link></li>
                <li><Link href="/community">Сообщество</Link></li>
              </ul>
            </div>
            
            <div className="footer-links-column">
              <h3>Компания</h3>
              <ul>
                <li><Link href="/about">О нас</Link></li>
                <li><Link href="/careers">Карьера</Link></li>
                <li><Link href="/contact">Контакты</Link></li>
                <li><Link href="/press">Пресса</Link></li>
              </ul>
            </div>
            
            <div className="footer-links-column">
              <h3>Правовое</h3>
              <ul>
                <li><Link href="/privacy">Конфиденциальность</Link></li>
                <li><Link href="/terms">Условия использования</Link></li>
                <li><Link href="/cookies">Политика файлов cookie</Link></li>
                <li><Link href="/license">Лицензия</Link></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p className="copyright">&copy; {new Date().getFullYear()} DevCommerce. Все права защищены.</p>
          <div className="language-selector">
            <select defaultValue="ru">
              <option value="ru">Русский</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 