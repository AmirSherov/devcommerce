import './projects.scss';
import DashboardLayout from '../../components/ui/dashboard-layout';
import { getAllProjects } from '../../api/projectspage/api';
import ProjectsGrid from './(components)/ProjectsGrid';
import { cookies } from 'next/headers';

export default async function ProjectsPage(){
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;
    const projects = await getAllProjects(token);
    return (
        <DashboardLayout activePage="projects">
            <div className="projects-page">
                <div className="projects-page__header">
                    <h1 className="projects-page__title">Проекты</h1>
                    <p className="projects-page__subtitle">Исследуйте удивительные проекты разработчиков</p>
                </div>
                <ProjectsGrid projects={projects && projects.results ? projects.results : []} token={token} />
            </div>
        </DashboardLayout>
    )
}