// Base URL of the backend. Empty = same origin (Vite dev proxy, or the API serving the built UI).
export const API = import.meta.env.VITE_API_URL ?? '';

const SESSION_KEY = 'cst-session-id';

// One id per browser; the server keeps this browser's uploads, outputs and logs under it.
export function getSessionId() {
    let id = null;
    try { id = localStorage.getItem(SESSION_KEY); } catch { /* storage blocked: fall back to a per-page id */ }
    if (!id) {
        id = crypto.randomUUID?.() ?? `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}-${Math.random().toString(16).slice(2)}`;
        try { localStorage.setItem(SESSION_KEY, id); } catch { /* ignore */ }
    }
    return id;
}

// fetch() that always identifies the session. `path` starts with /api or /logs.
export function apiFetch(path, options = {}) {
    const headers = { ...(options.headers || {}), 'X-Session-Id': getSessionId() };
    return fetch(`${API}${path}`, { ...options, headers });
}

// URL for places that cannot set headers (download links, EventSource).
export function sidUrl(path) {
    const sep = path.includes('?') ? '&' : '?';
    return `${API}${path}${sep}sid=${encodeURIComponent(getSessionId())}`;
}

// Readable message from a failed response (FastAPI sends {detail: string | [...]}).
export async function errorMessage(res) {
    try {
        const body = await res.json();
        if (typeof body.detail === 'string') return body.detail;
        if (Array.isArray(body.detail)) return body.detail.map(d => d.msg).join('; ');
    } catch { /* not JSON */ }
    return `Request failed (${res.status})`;
}
