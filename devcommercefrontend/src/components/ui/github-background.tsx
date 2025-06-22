"use client";
import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

export const GitHubBackground: React.FC = () => {
  const [isClient, setIsClient] = useState(false);
  const [binaryStrings, setBinaryStrings] = useState<string[]>([]);
  
  const codeStrings = [
    "npm install react",
    "git commit -m 'feat: add new feature'",
    "docker build -t app .",
    "const result = await fetch('/api')",
    "export default function Component()",
    "yarn add @types/node",
    "curl -X POST https://api.github.com",
    "import { useState } from 'react'",
    "npm run build && npm start",
    "git push origin main"
  ];

  useEffect(() => {
    setIsClient(true);
    // Generate binary strings only on client
    const newBinaryStrings = Array.from({ length: 15 }, () => 
      Array.from({ length: 50 }, () => Math.random() > 0.5 ? '1' : '0').join('')
    );
    setBinaryStrings(newBinaryStrings);
  }, []);

  if (!isClient) {
    return <div className="absolute inset-0" />; 
  }

  return (
    <div className="absolute inset-0 overflow-hidden">
      <div className="absolute inset-0">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-green-400/20 font-mono text-sm whitespace-nowrap"
            initial={{ y: -50, x: `${i * 15}%` }}
            animate={{ y: '100vh' }}
            transition={{
              duration: 15 + (i * 2), 
              repeat: Infinity,
              ease: 'linear',
              delay: i * 2,
            }}
          >
            {codeStrings[i % codeStrings.length]}
          </motion.div>
        ))}
      </div>
      <div className="absolute inset-0">
        {binaryStrings.map((binaryString, i) => (
          <motion.div
            key={`binary-${i}`}
            className="absolute text-blue-500/10 font-mono text-xs"
            initial={{ y: -100, x: `${i * 7}%` }}
            animate={{ y: '100vh' }}
            transition={{
              duration: 20 + (i * 2), 
              repeat: Infinity,
              ease: 'linear',
              delay: i * 0.5, 
            }}
          >
            {binaryString}
          </motion.div>
        ))}
      </div>

      {/* Geometric Shapes */}
      <div className="absolute inset-0">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={`shape-${i}`}
            className="absolute border border-indigo-500/20 rounded-lg"
            style={{
              width: `${50 + i * 20}px`,
              height: `${50 + i * 20}px`,
              left: `${10 + i * 15}%`,
              top: `${20 + i * 10}%`,
            }}
            animate={{
              rotate: 360,
              scale: [1, 1.1, 1],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 10 + i * 2,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        ))}
      </div>

      {/* Glowing Orbs */}
      <div className="absolute inset-0">
        {[...Array(4)].map((_, i) => (
          <motion.div
            key={`orb-${i}`}
            className="absolute rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 blur-xl"
            style={{
              width: `${100 + i * 50}px`,
              height: `${100 + i * 50}px`,
              left: `${20 + i * 20}%`,
              top: `${30 + i * 15}%`,
            }}
            animate={{
              x: [0, 50, -50, 0],
              y: [0, -30, 30, 0],
              scale: [1, 1.2, 0.8, 1],
            }}
            transition={{
              duration: 15 + i * 3,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 2,
            }}
          />
        ))}
      </div>

      {/* Network Lines */}
      <svg className="absolute inset-0 w-full h-full opacity-20">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0" />
            <stop offset="50%" stopColor="#6366f1" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[...Array(10)].map((_, i) => (
          <motion.line
            key={`line-${i}`}
            x1={`${i * 10}%`}
            y1="0%"
            x2={`${100 - i * 10}%`}
            y2="100%"
            stroke="url(#lineGradient)"
            strokeWidth="1"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 0.2,
            }}
          />
        ))}
      </svg>

      {/* Pulsing Dots Grid */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'radial-gradient(circle, #6366f1 1px, transparent 1px)',
          backgroundSize: '30px 30px',
          animation: 'pulse-grid 4s ease-in-out infinite'
        }}
      />
    </div>
  );
};

const cssAnimations = `
  @keyframes pulse-grid {
    0%, 100% { opacity: 0.2; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.05); }
  }
`;

if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = cssAnimations;
  document.head.appendChild(style);
} 