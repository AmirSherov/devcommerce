"use client";
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

const AnimatedInput = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, value, onChange, ...props }, ref) => {
    const [focused, setFocused] = useState(false);
    const [hasValue, setHasValue] = useState(false);

    // Update hasValue when value prop changes
    useEffect(() => {
      setHasValue(value !== undefined && value !== "");
    }, [value]);

    const handleFocus = () => setFocused(true);
    
    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(false);
      setHasValue(e.target.value !== "");
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setHasValue(e.target.value !== "");
      if (onChange) {
        onChange(e);
      }
    };

    return (
      <div className={`relative group ${className || ''}`}>
        {/* Анимированный фон */}
        <motion.div
          className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          initial={{ opacity: 0 }}
          animate={{ opacity: focused ? 1 : 0 }}
          transition={{ duration: 0.3 }}
        />
        
        {/* Светящаяся граница */}
        <motion.div
          className="absolute inset-0 rounded-lg border-2 border-transparent bg-gradient-to-r from-blue-500 to-purple-500 opacity-0"
          style={{
            background: focused 
              ? 'linear-gradient(90deg, #3b82f6, #8b5cf6) border-box'
              : 'transparent',
            WebkitMask: 'linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'subtract'
          }}
          animate={{
            opacity: focused ? 1 : 0,
            scale: focused ? 1.02 : 1
          }}
          transition={{ duration: 0.2 }}
        />

        {/* Основной контейнер */}
        <div className="relative bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-lg transition-all duration-300 hover:border-gray-600">
          {label && (
            <motion.label
              className={`absolute left-3 font-medium pointer-events-none transition-all duration-300 z-10 ${
                focused || hasValue 
                  ? 'top-1 text-xs text-blue-400 bg-gray-900/80 px-1 rounded' 
                  : 'top-4 text-sm text-gray-400'
              }`}
              animate={{
                y: focused || hasValue ? 0 : 0,
                scale: focused || hasValue ? 0.9 : 1,
                color: focused ? '#60a5fa' : hasValue ? '#9ca3af' : '#6b7280'
              }}
              transition={{ duration: 0.2 }}
            >
              {label}
            </motion.label>
          )}
          
          <input
            type={type}
            className={`w-full bg-transparent text-white border-none outline-none transition-all duration-300 ${
              label ? 'pt-7 pb-3 px-3' : 'py-4 px-3'
            } ${focused || hasValue ? 'placeholder-transparent' : 'placeholder-gray-500'}`}
            ref={ref}
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            {...props}
          />
          
          {/* Анимированная нижняя линия */}
          <motion.div
            className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500"
            initial={{ width: 0 }}
            animate={{ width: focused ? '100%' : '0%' }}
            transition={{ duration: 0.3 }}
          />
          
          {/* Частицы при фокусе */}
          {focused && (
            <div className="absolute inset-0 pointer-events-none">
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 bg-blue-400 rounded-full"
                  style={{
                    left: `${20 + i * 30}%`,
                    top: '50%'
                  }}
                  animate={{
                    y: [-10, -20, -10],
                    opacity: [0, 1, 0],
                    scale: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: i * 0.2
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }
);

AnimatedInput.displayName = "AnimatedInput";

export { AnimatedInput }; 