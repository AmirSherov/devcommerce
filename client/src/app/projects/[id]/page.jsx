'use client';
import './view.scss';
import { useParams } from 'next/navigation';
import DashboardLayout from '../../../components/ui/dashboard-layout';
import { getProjectDetail, getRecommendedProjects } from '../../../api/projectdetail/api';
import { useEffect, useState } from 'react';
import SimpleLoader from '@/components/simple-loader';
import { getAuthToken } from '@/lib/auth-utils';
import Link from 'next/link';
import { FaArrowRight, FaArrowLeft } from "react-icons/fa";
import { IoMdHeart } from "react-icons/io";
import ProjectComments from '../(components)/comments';
import { useAuth } from '@/contexts/AuthContext';

function ProjectDetailViewPage() {
    const { id } = useParams();
    const [isLoading, setIsLoading] = useState(true);
    const [project, setProject] = useState(null);
    const [recommended, setRecommended] = useState([]);
    const token = typeof window !== 'undefined' ? getAuthToken() : '';
    const { user } = useAuth();

    useEffect(() => {
        async function fetchData() {
            setIsLoading(true);
            const detail = await getProjectDetail(id, token);
            setProject(detail.project);
            const rec = await getRecommendedProjects(id, token);
            setRecommended(rec.results || []);
            setIsLoading(false);
        }
        if (id) fetchData();
    }, [id]);

    if (isLoading || !project) {
        return <SimpleLoader />;
    }

    return (
        <DashboardLayout activePage="projects">
            <div style={{position: 'relative',width:"40px",alignItems: 'center', justifyContent: 'center', display: 'flex', background: 'black',border: '1px solid white', height: '60px',padding: '10px',borderRadius: '10px',margin: '10px',cursor: 'pointer',transition: 'all 0.3s ease',}} className='project-view-root-back-to-list-flex'>
                    <Link href="/projects" className='project-view-root-back-to-list-link-flex'>
                        <FaArrowLeft />
                    </Link>
                </div>
            <div className="project-view-root-flex">
                <div className="project-view-main-flex">
                    <div className="project-view-top-flex">
                        <div className="project-view-image-block-flex">
                            <img className="project-view-image-flex" src={project.project_photo || '/template.png'} alt={project.title} />
                        </div>
                        <div className="project-view-info-flex">
                            <h1 className="project-view-title-flex">{project.title}</h1>
                            <div className="project-view-meta-flex">
                                <span className="project-view-author-flex">{project.author.full_name || project.author.username}</span>
                                <span className="project-view-dot">•</span>
                                <span className="project-view-views-flex">
                                  <span className="icon-eye" style={{fontSize: '1.1em', verticalAlign: 'middle'}}>👁</span>
                                  <span style={{marginLeft: 4}}>{project.views}</span>
                                </span>
                                <span className="project-view-dot">•</span>
                                <span className="project-view-likes-flex">
                                  <span style={{display: 'inline-flex', alignItems: 'center', gap: '4px'}}>
                                    <IoMdHeart style={{color: project.is_liked_by_user ? 'red' : '#aaa', fontSize: '1.15em', verticalAlign: 'middle'}} />
                                    <span>{project.likes}</span>
                                  </span>
                                </span>
                            </div>
                            <div className="project-view-technologies-flex">
                                {project.technologies && project.technologies.map((tech, i) => (
                                    <span className="project-view-tech-flex" key={i}>{tech}</span>
                                ))}
                            </div>
                            <div className="project-view-links-flex">
                                {project.github_link && <a href={project.github_link} target="_blank" rel="noopener noreferrer">GitHub</a>}
                                {project.project_public_link && <a href={project.project_public_link} target="_blank" rel="noopener noreferrer">Live</a>}
                            </div>
                            <div className="project-view-description-flex">{project.description}</div>
                        </div>
                    </div>
                    <ProjectComments projectId={project.id} token={token} canPin={user && project.author.id === user.id} userId={user ? user.id : null} />
                </div>
                <div className="project-view-sidebar-flex">
                    <h3 className="project-view-sidebar-title-flex">Рекомендованные проекты</h3>
                    <div className="project-view-recommended-list-flex">
                        {recommended.length === 0 && <div className="project-view-recommended-empty-flex">Нет рекомендаций</div>}
                        {recommended.map((rec) => (
                            <Link href={`/projects/${rec.id}`} className="project-view-recommended-card-flex" key={rec.id}>
                                <img className="project-view-recommended-img-flex" src={rec.project_photo || '/template.png'} alt={rec.title} />
                                <div className="project-view-recommended-info-flex">
                                    <span className="project-view-recommended-title-flex">{rec.title}</span>
                                    <div className="project-view-recommended-author-flex">{rec.author.full_name || rec.author.username}</div>
                                </div>
                                <span className='project-view-recommended-arrow-flex'>
                                <FaArrowRight />
                                </span>
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
export default ProjectDetailViewPage;