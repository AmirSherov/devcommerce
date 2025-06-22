"use client";
import React, { useState } from "react";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

const AnimatedInput = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, ...props }, ref) => {
    const [focused, setFocused] = useState(false);
    const [hasValue, setHasValue] = useState(false);

    const handleFocus = () => setFocused(true);
    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(false);
      setHasValue(e.target.value !== "");
    };

    return (
      <div className={`animated-input ${className || ''}`}>
        {label && (
          <label
            className={`input-label ${focused || hasValue ? 'focused has-value' : ''}`}
          >
            {label}
          </label>
        )}
        <input
          type={type}
          className="input-field"
          ref={ref}
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...props}
        />
        
        <div className={`input-border ${focused ? 'active' : ''}`} />
      </div>
    );
  }
);

AnimatedInput.displayName = "AnimatedInput";

export { AnimatedInput }; 