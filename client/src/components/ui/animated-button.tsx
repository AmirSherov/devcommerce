"use client";
import React, { useState } from "react";
import tailwindcss from '@tailwindcss/postcss';
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "social";
  children: React.ReactNode;
}

const AnimatedButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", children, ...props }, ref) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
      <button
        ref={ref}
        className={`animated-button ${variant} ${className || ''}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        {...props}
      >
        {/* Animated background overlay */}
        {variant === "primary" && (
          <div className={`button-overlay ${isHovered ? 'active' : ''}`} />
        )}
        
        {/* Ripple effect */}
        <div className={`button-ripple ${isHovered ? 'active' : ''}`} />
        
        {/* Content */}
        <span className="button-content">
          {children}
        </span>
      </button>
    );
  }
);

AnimatedButton.displayName = "AnimatedButton";

export { AnimatedButton }; 