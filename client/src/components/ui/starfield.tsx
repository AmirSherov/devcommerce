"use client";
import React, { useEffect, useRef } from 'react';
import tailwindcss from '@tailwindcss/postcss';
export const Starfield: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;

    const setCanvasSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // Stars array
    const stars: Array<{
      x: number;
      y: number;
      radius: number;
      opacity: number;
      speed: number;
      twinkleSpeed: number;
      color: string;
    }> = [];

    // Create stars
    const createStars = () => {
      const starCount = 150;
      const colors = ['#ffffff', '#b3d9ff', '#ffd9b3', '#ffb3b3', '#d9b3ff'];
      
      for (let i = 0; i < starCount; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          radius: Math.random() * 2 + 0.5,
          opacity: Math.random() * 0.8 + 0.2,
          speed: Math.random() * 0.5 + 0.1,
          twinkleSpeed: Math.random() * 0.02 + 0.01,
          color: colors[Math.floor(Math.random() * colors.length)],
        });
      }
    };
    createStars();

    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      time += 0.01;

      stars.forEach((star) => {
        // Update star position (slow drift)
        star.x += star.speed * 0.1;
        star.y += star.speed * 0.05;

        // Wrap around edges
        if (star.x > canvas.width) star.x = 0;
        if (star.y > canvas.height) star.y = 0;

        // Twinkling effect
        const twinkle = Math.sin(time * star.twinkleSpeed) * 0.5 + 0.5;
        const currentOpacity = star.opacity * twinkle;

        // Draw star with glow effect
        ctx.save();
        
        // Outer glow
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius * 3, 0, Math.PI * 2);
        ctx.fillStyle = `${star.color}15`; // Very transparent
        ctx.fill();

        // Middle glow
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = `${star.color}40`; // Semi-transparent
        ctx.fill();

        // Core star
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = star.color + Math.floor(currentOpacity * 255).toString(16).padStart(2, '0');
        ctx.fill();

        ctx.restore();
      });

      animationId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      window.removeEventListener('resize', setCanvasSize);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none opacity-60"
      style={{ background: 'transparent' }}
    />
  );
}; 