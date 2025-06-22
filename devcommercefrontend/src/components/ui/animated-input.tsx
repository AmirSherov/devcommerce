"use client";
import React, { useState, useEffect } from "react";

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
          value={value}
          onChange={handleChange}
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