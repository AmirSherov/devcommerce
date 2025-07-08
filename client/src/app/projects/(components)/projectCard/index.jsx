import React, { useState } from 'react';
import './style.scss';
import { toggleProjectLike } from '../../../../api/projectspage/api';
import Link from 'next/link';
const ProjectCard = ({ project, token }) => {
  const {
    title,
    description,
    project_photo,
    technologies,
    live_url,
    github_url,
    created_at,
    likes: initialLikes,
    views,
    is_liked_by_user: initialLiked
  } = project;

  const [likes, setLikes] = useState(initialLikes);
  const [liked, setLiked] = useState(initialLiked || false);
  const [loading, setLoading] = useState(false);

  async function handleLike() {
    if (loading) return;
    setLoading(true);
    try {
      const res = await toggleProjectLike(project.id, token);
      if (liked) {
        setLikes(likes - 1);
      } else {
        setLikes(likes + 1);
      }
      setLiked(!liked);
    } catch (e) {
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="project-card">
      <div className="project-card__image">
        <img src={project_photo || '/template.png'} alt={title} />
      </div>
      
      <div className="project-card__content">
        <Link href={`/projects/${project.id}`}>
        <h3 className="project-card__title">{title}</h3>
        </Link>
        <p className="project-card__description">{description}</p>
        
        <div className="project-card__technologies">
          {technologies && technologies.slice(0, 4).map((tech, index) => (
            <span key={index} className="project-card__tech">
              {tech}
            </span>
          ))}
          {technologies && technologies.length > 4 && (
            <span className="project-card__tech project-card__tech--more">
              +{technologies.length - 4}
            </span>
          )}
        </div>
        
        <div className="project-card__stats">
          <div className="project-card__stat">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            <span>{views || 0}</span>
          </div>
          <div className="project-card__stat" style={{cursor: 'pointer'}} onClick={handleLike}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill={liked ? '#ef4444' : 'none'} stroke={liked ? '#ef4444' : 'currentColor'} strokeWidth="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
            <span>{likes}</span>
          </div>
          <div className="project-card__stat">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12,6 12,12 16,14"/>
            </svg>
            <span>{new Date(created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;
