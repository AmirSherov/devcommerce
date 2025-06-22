"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import "./style.scss";

const Newsletter = () => {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (email) {
      // Здесь будет логика отправки email на сервер
      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        setEmail("");
      }, 3000);
    }
  };
  
  return (
    <section className="newsletter-section">
      <div className="newsletter-container">
        <div className="newsletter-content">
          <div className="newsletter-text">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              Получайте последние обновления
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              Подпишитесь на нашу рассылку, чтобы получать информацию о новых продуктах, скидках и тенденциях в разработке
            </motion.p>
          </div>
          
          <motion.form
            className="newsletter-form"
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="form-group">
              <input
                type="email"
                placeholder="Введите ваш email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={submitted}
              />
              <button 
                type="submit"
                disabled={submitted}
              >
                {submitted ? (
                  <div className="success-message">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    Готово
                  </div>
                ) : (
                  'Подписаться'
                )}
              </button>
            </div>
            <p className="privacy-note">Мы не отправляем спам. Читайте нашу <a href="/privacy">политику конфиденциальности</a></p>
          </motion.form>
        </div>
        
        <div className="newsletter-decoration">
          <svg width="100%" height="100%" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <path fill="#58a6ff" d="M43.8,-57.5C58.4,-52.9,73.2,-43.6,77.8,-30.5C82.5,-17.4,76.9,-0.5,72.4,15.7C67.9,32,64.4,47.6,54.7,58C45.1,68.5,29.3,73.8,14.1,74.8C-1.1,75.8,-15.8,72.5,-26,64.2C-36.3,55.9,-42,42.6,-47.2,30.7C-52.4,18.8,-57.1,8.3,-57.8,-2.6C-58.5,-13.5,-55.2,-25.4,-48.6,-35C-42,-44.5,-32,-51.7,-21,-56.7C-10,-61.7,1.9,-64.5,13.7,-64.2C25.5,-63.8,37.2,-60.1,43.8,-57.5Z" transform="translate(100 100)" />
          </svg>
          <motion.div 
            className="dot-pattern"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 0.5 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          ></motion.div>
        </div>
      </div>
    </section>
  );
};

export default Newsletter; 