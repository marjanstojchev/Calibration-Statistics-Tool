import { useState } from 'react';
import { apiFetch, sidUrl, errorMessage } from '../api';
const CalcIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="10" x2="16" y2="14"/><line x1="8" y1="10" x2="12" y2="10"/><line x1="8" y1="14" x2="12" y2="14"/><line x1="8" y1="18" x2="16" y2="18"/></svg>;
const TrashIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>;
export default function LimitsTab() {
    const [limitsType, setLimitsType] = useState('burn_in');
    const [extendLimits, setExtendLimits] = useState(false);
    const [extendGroups, setExtendGroups] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [notice, setNotice] = useState(null);
    const [exported, setExported] = useState(null);
    const [rows, setRows] = useState([]);
    const [groups, setGroups] = useState([]);

    const prefix = limitsType === 'burn_in' ? 'burn_in' : 'cal';

    const handleCompute = async () => {
        setLoading(true); setResult(null); setNotice(null); setExported(null);
        try {
            const res = await apiFetch('/api/limits/compute', { method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limits_type: limitsType, extend_input_limits: extendLimits, extend_limits_groups: extendGroups }) });
            if (!res.ok) { setResult({ error: await errorMessage(res) }); setRows([]); setGroups([]); }
            else {
                const data = await res.json(); setResult(data);
                const [rr, gr] = await Promise.all([apiFetch('/api/limits/rows').then(r=>r.json()), apiFetch('/api/limits/groups').then(r=>r.json())]);
                setRows(rr.rows??[]); setGroups(gr.groups??[]);
            }
        } catch (err) { setResult({ error: err.message }); }
        setLoading(false);
    };

    const handleClear = async () => {
        setLoading(true);
        try {
            const res = await apiFetch('/api/limits/clear', { method: 'DELETE' });
            if (!res.ok) { setResult({ error: await errorMessage(res) }); }
            else { setResult(null); setNotice(null); setExported(null); setRows([]); setGroups([]); }
        } catch (err) { setResult({ error: err.message }); }
        setLoading(false);
    };

    const handleConfigUpload = async (name, file) => {
        if (!file) return;
        setLoading(true); setNotice(null);
        try {
            const body = new FormData();
            body.append('file', file);
            const res = await apiFetch(`/api/limits/config/${name}`, { method: 'POST', body });
            if (!res.ok) setResult({ error: await errorMessage(res) });
            else { setResult(null); setRows([]); setGroups([]); setNotice(`${file.name} is now used for this session. Compute again to apply it.`); }
        } catch (err) { setResult({ error: err.message }); }
        setLoading(false);
    };

    const handleConfigReset = async () => {
        setLoading(true); setNotice(null);
        try {
            const res = await apiFetch('/api/limits/config', { method: 'DELETE' });
            if (!res.ok) setResult({ error: await errorMessage(res) });
            else { setResult(null); setRows([]); setGroups([]); setNotice('Default limits and groups files restored. Compute again to apply them.'); }
        } catch (err) { setResult({ error: err.message }); }
        setLoading(false);
    };

    const handleExport = async () => {
        setLoading(true); setExported(null);
        try {
            const res = await apiFetch('/api/limits/export/pptx', { method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limits_type: limitsType }) });
            if (!res.ok) setResult({ error: await errorMessage(res) });
            else setExported((await res.json()).pptx_file);
        } catch (err) { setResult({ error: err.message }); }
        setLoading(false);
    };

    const fileInput = (name, label) => (
        <label className="btn btn-secondary" style={{ cursor: loading ? 'not-allowed' : 'pointer' }}>
            {label}
            <input type="file" accept=".yaml,.yml" style={{ display:'none' }} disabled={loading}
                onChange={e => { handleConfigUpload(name, e.target.files[0]); e.target.value = ''; }} />
        </label>
    );

    return (
        <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
            <div className="card">
                <div className="card-header"><h3><CalcIcon /> Limits Configuration</h3><button className="btn btn-ghost" onClick={handleClear} disabled={loading}><TrashIcon /> Clear</button></div>
                <div className="card-body" style={{ display:'flex', flexDirection:'column', gap:'var(--space-5)' }}>
                    <div className="section">
                        <div className="section-label">Protocol Type</div>
                        <div className="radio-group">
                            <label className="radio-item"><input type="radio" name="lt" value="burn_in" checked={limitsType==='burn_in'} onChange={() => setLimitsType('burn_in')} /> Burn-In</label>
                            <label className="radio-item"><input type="radio" name="lt" value="calibration" checked={limitsType==='calibration'} onChange={() => setLimitsType('calibration')} /> Calibration</label>
                        </div>
                    </div>
                    <div className="divider" />
                    <div className="section">
                        <div className="section-label">Limits and Groups Files (optional)</div>
                        <p style={{ margin: 0, fontSize:'var(--text-sm)', color:'var(--color-text-muted)' }}>
                            The server's default files are used unless you upload your own. Uploaded files only apply to your session.
                        </p>
                        <div className="btn-group" style={{ marginTop:'var(--space-2)' }}>
                            {fileInput(`${prefix}_limits`, 'Upload Limits YAML')}
                            {fileInput(`${prefix}_groups`, 'Upload Groups YAML')}
                            <button className="btn btn-ghost" onClick={handleConfigReset} disabled={loading}>Use Default Files</button>
                        </div>
                    </div>
                    <div className="section">
                        <label className="check-item"><input type="checkbox" checked={extendLimits} onChange={() => setExtendLimits(p=>!p)} /> Extend Input Limits</label>
                        <label className="check-item"><input type="checkbox" checked={extendGroups} onChange={() => setExtendGroups(p=>!p)} /> Extend Limits Groups</label>
                    </div>
                </div>
                <div className="card-footer">
                    <button className="btn btn-primary" onClick={handleCompute} disabled={loading}>
                        {loading ? <><span className="spinner" /> Working...</> : <><CalcIcon /> Compute Stats</>}
                    </button>
                    {rows.length > 0 && <button className="btn btn-secondary" onClick={handleExport} disabled={loading}>Export PPTX</button>}
                </div>
            </div>
            {result?.error && <div className="alert alert-error">{result.error}</div>}
            {notice && <div className="alert alert-info">{notice}</div>}
            {result?.status === 'ok' && (
                <div className="alert alert-success">Computed {result.row_count} rows from {result.protocols_used} protocols ({limitsType})</div>
            )}
            {exported && (
                <div className="alert alert-success">
                    Exported: <a href={sidUrl(`/api/downloads/download/statistic/${exported}`)} download>{exported}</a>
                </div>
            )}
            {rows.length > 0 && (
                <div className="card">
                    <div className="card-header"><h3>Limits Rows ({rows.length})</h3></div>
                    <div className="card-body" style={{padding:0}}>
                        <div className="table-wrap" style={{borderRadius:0,border:'none'}}>
                            <table className="data-table">
                                <thead><tr><th>#</th><th>Name</th><th>Type</th><th>Lower</th><th>Upper</th><th>Mean</th><th>Min</th><th>Max</th><th>StDev</th><th>Cg</th></tr></thead>
                                <tbody>
                                    {rows.map((r,i) => (
                                        <tr key={i}><td>{r.index}</td><td>{r.limitName}</td><td>{r.protType}</td><td>{r.lowerLimit}</td><td>{r.upperLimit}</td><td>{r.mean}</td><td>{r.min}</td><td>{r.max}</td><td>{r.stDev}</td><td>{r.cg}</td></tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
            {groups.length > 0 && (
                <div className="card">
                    <div className="card-header"><h3>Limits Groups ({groups.length})</h3></div>
                    <div className="card-body">
                        <div className="stats-grid">
                            {groups.map((g,i) => <div key={i} className="stat-card"><div className="stat-label" style={{fontWeight:600,fontSize:'var(--text-base)'}}>{g.name}</div><div className="stat-label">{g.protType}</div></div>)}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
