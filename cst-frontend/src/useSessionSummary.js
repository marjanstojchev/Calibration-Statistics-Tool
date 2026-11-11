import { useCallback, useEffect, useState } from 'react';
import { apiFetch } from './api';

// What the server holds for this browser's session (file counts). Returns [summary, refresh].
export function useSessionSummary() {
    const [summary, setSummary] = useState(null);
    const refresh = useCallback(async () => {
        try {
            const res = await apiFetch('/api/session');
            if (res.ok) setSummary(await res.json());
        } catch { /* backend not reachable: keep the last value */ }
    }, []);
    useEffect(() => {
        let alive = true;
        apiFetch('/api/session')
            .then(res => (res.ok ? res.json() : null))
            .then(data => { if (alive && data) setSummary(data); })
            .catch(() => {});
        return () => { alive = false; };
    }, []);
    return [summary, refresh];
}
