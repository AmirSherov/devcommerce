const API_BASE_URL = 'http://127.0.0.1:8000/api';
import { getAuthHeaders } from "@/lib/auth-utils";

export async function getProjectDetail(projectId, token) {
    const request = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
        headers: {
            'Authorization': `Bearer ${token || ''}`
        }
    });
    return await request.json();
}

export async function getRecommendedProjects(projectId, token) {
    const request = await fetch(`${API_BASE_URL}/projects/recommended/${projectId}/`, {
        headers: {
            'Authorization': `Bearer ${token || ''}`
        }
    });
    return await request.json();
}