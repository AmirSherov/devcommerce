const API_BASE_URL = 'http://127.0.0.1:8000/api';
import { getAuthHeaders } from "@/lib/auth-utils";

export async function getAllProjects(token) {
    const request = await fetch(`${API_BASE_URL}/projects/`, {
        headers: {
            'Authorization': `Bearer ${token || ''}`
        }
    });
    return await request.json();
}

export async function toggleProjectLike(projectId , token){

    const request = await fetch(`${API_BASE_URL}/projects/toggle-like/${projectId}/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        },
        method: 'POST'
    });
}