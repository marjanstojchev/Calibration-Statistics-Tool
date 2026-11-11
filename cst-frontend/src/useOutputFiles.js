import { useCallback, useEffect, useState } from 'react';
import { apiFetch } from './api';

// Files the server holds for this session in one output folder. They survive a page reload,
// so the list is loaded on mount and can be refreshed after a generation.
export function useOutputFiles(kind, recursive = false) {
    const path = `/api/downloads/list/${kind}${recursive ? '/recursive' : ''}`;
    const [files, setFiles] = useState([]);

    const refresh = useCallback(async () => {
        try {
            const res = await apiFetch(path);
            if (res.ok) setFiles((await res.json()).files ?? []);
        } catch { /* backend not reachable */ }
    }, [path]);

    useEffect(() => {
        let alive = true;
        apiFetch(path)
            .then(res => (res.ok ? res.json() : null))
            .then(data => { if (alive && data) setFiles(data.files ?? []); })
            .catch(() => {});
        return () => { alive = false; };
    }, [path]);

    return [files, setFiles, refresh];
}
