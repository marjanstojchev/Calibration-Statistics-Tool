import { useState, useEffect } from 'react';
const API = 'http://localhost:8000';
const RefreshIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.95"/></svg>;
const TrashIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>;
export default function StatisticsTab() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const fetchStats = async () => {
        setLoading(true);
        try { const res = await fetch(`${API}/api/protocol_stats/`); setStats(await res.json()); }
        catch (err) { setStats({ error: err.message }); }
        setLoading(false);
    };
    const handleClear = async () => { await fetch(`${API}/api/protocol_stats/clear`, { method: 'DELETE' }); await fetchStats(); };
    useEffect(() => { fetchStats(); }, []);
    return (
        <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
            <div className="card">
                <div className="card-header">
                    <h3>Statistics</h3>
                    <div className="btn-group">
                        <button className="btn btn-secondary" onClick={fetchStats} disabled={loading}><RefreshIcon /> Refresh</button>
                        <button className="btn btn-danger" onClick={handleClear}><TrashIcon /> Clear Data</button>
                    </div>
                </div>
                <div className="card-body">
                    {stats?.error && <div className="alert alert-error">{stats.error}</div>}
                    {stats && !stats.error && (
                        <div className="stats-grid">
                            <div className="stat-card"><div className="stat-value">{stats.sys_diag_ptu2_loaded}</div><div className="stat-label">System Diag. PTU2 Loaded</div></div>
                            <div className="stat-card"><div className="stat-value">{stats.tx_ant_diag_loaded}</div><div className="stat-label">TX Ant. Diag. Loaded</div></div>
                        </div>
                    )}
                </div>
            </div>
            <div className="card">
                <div className="card-header"><h3>Chart View</h3><span className="badge badge-warn">Coming Soon</span></div>
                <div className="card-body">
                    <div className="chart-placeholder">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>
                        <p>Statistical charts will appear here after computing limits</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
