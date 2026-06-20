import { useState } from 'react';
const API = 'http://localhost:8000';
const CalcIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="10" x2="16" y2="14"/><line x1="8" y1="10" x2="12" y2="10"/><line x1="8" y1="14" x2="12" y2="14"/><line x1="8" y1="18" x2="16" y2="18"/></svg>;
const TrashIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>;
export default function LimitsTab() {
    const [limitsType, setLimitsType] = useState('burn_in');
    const [inputLimitsPath, setInputLimitsPath] = useState('');
    const [limitsGroupsPath, setLimitsGroupsPath] = useState('');
    const [extendLimits, setExtendLimits] = useState(false);
    const [extendGroups, setExtendGroups] = useState(false);
    const [activeLimitsGroup, setActiveLimitsGroup] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [rows, setRows] = useState([]);
    const [groups, setGroups] = useState([]);
    const handleCompute = async () => {
        setLoading(true); setResult(null);
        try {
            const res = await fetch(`${API}/api/limits/compute`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limits_type: limitsType, input_limits_file_path: inputLimitsPath, extend_input_limits: extendLimits, limits_groups_file_path: limitsGroupsPath, extend_limits_groups: extendGroups, active_limits_group: activeLimitsGroup }) });
            const data = await res.json(); setResult(data);
            if (data.status === 'ok') {
                const [rr, gr] = await Promise.all([fetch(`${API}/api/limits/rows`).then(r=>r.json()), fetch(`${API}/api/limits/groups`).then(r=>r.json())]);
                setRows(rr.rows??[]); setGroups(gr.groups??[]);
            }
        } catch (err) { setResult({ error: err.message }); }
        setLoading(false);
    };
    const handleClear = async () => { await fetch(`${API}/api/limits/clear`, { method: 'DELETE' }); setResult(null); setRows([]); setGroups([]); };
    return (
        <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
            <div className="card">
                <div className="card-header"><h3><CalcIcon /> Limits Configuration</h3><button className="btn btn-ghost" onClick={handleClear}><TrashIcon /> Clear</button></div>
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
                        <div className="section-label">Input Limits File</div>
                        <div className="form-group">
                            <input className="input" type="text" value={inputLimitsPath} onChange={e => setInputLimitsPath(e.target.value)} placeholder="C:\path\to\limits.yaml" />
                        </div>
                        <div style={{marginTop:'var(--space-2)'}}>
                            <label className="check-item"><input type="checkbox" checked={extendLimits} onChange={() => setExtendLimits(p=>!p)} /> Extend Input Limits</label>
                        </div>
                    </div>
                    <div className="section">
                        <div className="section-label">Limits Groups File</div>
                        <div className="form-group">
                            <input className="input" type="text" value={limitsGroupsPath} onChange={e => setLimitsGroupsPath(e.target.value)} placeholder="C:\path\to\groups.yaml" />
                        </div>
                        <div style={{marginTop:'var(--space-2)'}}>
                            <label className="check-item"><input type="checkbox" checked={extendGroups} onChange={() => setExtendGroups(p=>!p)} /> Extend Limits Groups</label>
                        </div>
                    </div>
                    <div className="section">
                        <div className="section-label">Active Limits Group</div>
                        <input className="input" type="text" value={activeLimitsGroup} onChange={e => setActiveLimitsGroup(e.target.value)} placeholder="Group name (optional)" />
                    </div>
                </div>
                <div className="card-footer">
                    <button className="btn btn-primary" onClick={handleCompute} disabled={loading || !inputLimitsPath || !limitsGroupsPath}>
                        {loading ? <><span className="spinner" /> Computing...</> : <><CalcIcon /> Compute Stats</>}
                    </button>
                </div>
            </div>
            {result?.error && <div className="alert alert-error">{result.error}</div>}
            {result?.detail && <div className="alert alert-error">{result.detail}</div>}
            {result?.status === 'ok' && (
                <div className="alert alert-success">Computed {result.row_count} rows ({limitsType})</div>
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
