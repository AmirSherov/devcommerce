const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
import { getAuthHeaders, getSessionHeaders } from "@/lib/auth-utils";

export async function getProjectDetail(projectId, token) {
    const request = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token || ''}`,
            ...getAuthHeaders(),
            ...getSessionHeaders(),
        }
    });
    return await request.json();
}

export async function getRecommendedProjects(projectId, token) {
    const request = await fetch(`${API_BASE_URL}/projects/recommended/${projectId}/`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token || ''}`,
            ...getAuthHeaders(),
            ...getSessionHeaders(),
        }
    });
    return await request.json();
}