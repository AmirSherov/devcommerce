import React from 'react';

const SimpleLoader = ({ 
  size = 'h-12 w-12', 
  text, 
  className = '',
  fullScreen = true 
}) => {
  const containerClasses = fullScreen 
    ? "min-h-screen flex items-center justify-center bg-black"
    : "flex items-center justify-center";

  return (
    <div className={`${containerClasses} ${className}`}>
      <div className="flex flex-col items-center space-y-4">
        <div className={`animate-spin rounded-full ${size} border-b-2 border-white`}></div>
        {text && (
          <p className="text-white text-sm font-medium">{text}</p>
        )}
      </div>
    </div>
  );
};

export default SimpleLoader; 