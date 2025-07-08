const API_BASE_URL = 'http://127.0.0.1:8000/api/projects';

export async function fetchProjectComments(projectId, token) {
    const res = await fetch(`${API_BASE_URL}/${projectId}/comments/`, {
        headers: { 'Authorization': `Bearer ${token || ''}` }
    });
    return await res.json();
}

export async function createProjectComment(projectId, data, token) {
    const res = await fetch(`${API_BASE_URL}/${projectId}/comments/create/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token || ''}`
        },
        body: JSON.stringify(data)
    });
    return await res.json();
}

export async function editProjectComment(commentId, data, token) {
    const res = await fetch(`${API_BASE_URL}/comments/${commentId}/edit/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token || ''}`
        },
        body: JSON.stringify(data)
    });
    return await res.json();
}

export async function deleteProjectComment(commentId, token) {
    const res = await fetch(`${API_BASE_URL}/comments/${commentId}/delete/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token || ''}` }
    });
    return await res.json();
}

export async function likeProjectComment(commentId, token) {
    const res = await fetch(`${API_BASE_URL}/comments/${commentId}/like/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token || ''}` }
    });
    return await res.json();
}

export async function pinProjectComment(commentId, token) {
    const res = await fetch(`${API_BASE_URL}/comments/${commentId}/pin/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token || ''}` }
    });
    return await res.json();
} 