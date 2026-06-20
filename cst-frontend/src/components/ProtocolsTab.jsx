import { useState, useRef } from 'react';
const API = 'http://localhost:8000';
const UploadIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>;
const FolderIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>;
const FileIcon = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>;
const TrashIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>;
export default function ProtocolsTab() {
    const [files, setFiles] = useState(null);
    const [filters, setFilters] = useState({ search_ptu2_files: true, search_txantdiag_files: false, latest_protocol: false, burn_in_start: false, use_error: false, use_abort: true, use_limits_exceeded: true, protocol_type: 'auto' });
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [discoveredFiles, setDiscoveredFiles] = useState({ protocols: [], ptu2: [], txantdiag: [] });
    const ptu2InputRef = useRef(null);
    const txantInputRef = useRef(null);
    const handleBrowseDirectory = async () => {
        try {
            const dirHandle = await window.showDirectoryPicker();
            const discovered = { protocols: [], ptu2: [], txantdiag: [] };
            const searchDir = async (dir) => {
                for await (const entry of dir.values()) {
                    if (entry.kind === 'file') {
                        const n = entry.name.toLowerCase();
                        if (n.includes('_ptu2')) discovered.ptu2.push(entry);
                        else if (n.includes('_txantdiag')) discovered.txantdiag.push(entry);
                        else if (n.endsWith('.txt')) discovered.protocols.push(entry);
                    } else if (entry.kind === 'directory') { try { await searchDir(entry); } catch(_){} }
                }
            };
            await searchDir(dirHandle);
            setDiscoveredFiles(discovered);
            setFiles(await Promise.all(discovered.protocols.map(h => h.getFile())));
        } catch (err) { if (err.name !== 'AbortError') console.error(err); }
    };
    const handlePTU2FileSelect = (e) => {
        const sel = Array.from(e.target.files);
        const existing = discoveredFiles.ptu2.map(f => f.name);
        const newF = sel.filter(f => !existing.includes(f.name));
        if (newF.length) setDiscoveredFiles(prev => ({ ...prev, ptu2: [...prev.ptu2, ...newF] }));
    };
    const handleTxAntDiagFileSelect = (e) => {
        const sel = Array.from(e.target.files);
        const existing = discoveredFiles.txantdiag.map(f => f.name);
        const newF = sel.filter(f => !existing.includes(f.name));
        if (newF.length) setDiscoveredFiles(prev => ({ ...prev, txantdiag: [...prev.txantdiag, ...newF] }));
    };
    const handleUpload = async () => {
        if (!files?.length) return;
        setLoading(true);
        try {
            const queryParams = new URLSearchParams();
            Object.entries(filters).forEach(([k, v]) => queryParams.append(k, v));
            const formData = new FormData();
            for (let f of files) formData.append('files', f);
            if (discoveredFiles.ptu2.length > 0) { const p = await Promise.all(discoveredFiles.ptu2.map(h => h.getFile ? h.getFile() : h)); for (let f of p) formData.append('ptu2_files', f); }
            if (discoveredFiles.txantdiag.length > 0) { const t = await Promise.all(discoveredFiles.txantdiag.map(h => h.getFile ? h.getFile() : h)); for (let f of t) formData.append('txantdiag_files', f); }
            const res = await fetch(`${API}/api/protocols/upload?${queryParams}`, { method: 'POST', body: formData });
            setResponse(await res.json());
        } catch (err) { setResponse({ error: err.message }); }
        setLoading(false);
    };
    const handleClear = async () => {
        await fetch(`${API}/api/protocols/clear`, { method: 'DELETE' });
        setResponse(null); setFiles(null); setDiscoveredFiles({ protocols: [], ptu2: [], txantdiag: [] });
    };
    const defaults = { search_ptu2_files: true, search_txantdiag_files: false, latest_protocol: false, burn_in_start: false, use_error: false, use_abort: true, use_limits_exceeded: true, protocol_type: 'auto' };
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="card">
                <div className="card-header">
                    <h3><FolderIcon /> Load Data</h3>
                    <button className="btn btn-ghost" onClick={handleClear}><TrashIcon /> Clear</button>
                </div>
                <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                    <div className="section">
                        <div className="section-label">Protocol Files</div>
                        <div className="btn-group">
                            <input type="file" multiple accept=".txt" id="proto-input" style={{ display:'none' }} onChange={e => setFiles(Array.from(e.target.files))} />
                            <label htmlFor="proto-input" className="btn btn-secondary" style={{ cursor:'pointer' }}><FileIcon /> Select Files</label>
                            <button className="btn btn-secondary" onClick={handleBrowseDirectory}><FolderIcon /> Browse & Scan Directory</button>
                        </div>
                        {(files?.length > 0 || discoveredFiles.ptu2.length > 0) && (
                            <div className="file-list">
                                {files?.length > 0 && <span className="badge badge-info"><FileIcon /> {files.length} protocol files</span>}
                                {discoveredFiles.ptu2.length > 0 && <span className="badge badge-success">{discoveredFiles.ptu2.length} PTU2</span>}
                                {discoveredFiles.txantdiag.length > 0 && <span className="badge badge-success">{discoveredFiles.txantdiag.length} TxAnt</span>}
                            </div>
                        )}
                    </div>
                    <div className="divider" />
                    <div className="section">
                        <div className="section-label">File Search Options</div>
                        <div className="check-group">
                            <label className="check-item"><input type="checkbox" checked={filters.search_ptu2_files} onChange={() => setFilters(p=>({...p,search_ptu2_files:!p.search_ptu2_files}))} /> Search PTU2 Files</label>
                            <label className="check-item"><input type="checkbox" checked={filters.search_txantdiag_files} onChange={() => setFilters(p=>({...p,search_txantdiag_files:!p.search_txantdiag_files}))} /> Search TxAnt. Diag. Files</label>
                        </div>
                    </div>
                    <div className="section">
                        <div className="section-label">Use Protocols With</div>
                        <div className="check-group">
                            {[['latest_protocol','Latest Protocol'],['burn_in_start','Burnin Start'],['use_error','EOL Error(s)'],['use_abort','EOL Abort Criterion(s)'],['use_limits_exceeded','EOL Meas. Limits Exceeded']].map(([k,l]) => (
                                <label key={k} className="check-item"><input type="checkbox" checked={filters[k]} onChange={() => setFilters(p=>({...p,[k]:!p[k]}))} /> {l}</label>
                            ))}
                        </div>
                    </div>
                    <div className="section">
                        <div className="section-label">Protocol Type</div>
                        <div className="radio-group">
                            {[['auto','Auto Recognition'],['burn_in','BurnIn'],['calibration','Calibration']].map(([v,l]) => (
                                <label key={v} className="radio-item"><input type="radio" name="prot_type" value={v} checked={filters.protocol_type===v} onChange={() => setFilters(p=>({...p,protocol_type:v}))} /> {l}</label>
                            ))}
                        </div>
                    </div>
                    <div className="section">
                        <div className="section-label">Add Files Separately</div>
                        <div className="btn-group">
                            <input id="ptu2-input" ref={ptu2InputRef} type="file" multiple accept=".txt" style={{display:'none'}} onChange={handlePTU2FileSelect} />
                            <input id="txant-input" ref={txantInputRef} type="file" multiple accept=".txt" style={{display:'none'}} onChange={handleTxAntDiagFileSelect} />
                            <button className="btn btn-secondary" onClick={() => ptu2InputRef.current?.click()}><FileIcon /> Add PTU2 Files</button>
                            <button className="btn btn-secondary" onClick={() => txantInputRef.current?.click()}><FileIcon /> Add TxAntDiag Files</button>
                        </div>
                    </div>
                </div>
                <div className="card-footer">
                    <button className="btn btn-primary" onClick={handleUpload} disabled={!files?.length||loading}>
                        {loading ? <><span className="spinner" /> Loading...</> : <><UploadIcon /> Load Protocols</>}
                    </button>
                    <button className="btn btn-secondary" onClick={() => setFilters(defaults)}>Use Defaults</button>
                </div>
            </div>
            {response && (
                <div className="card">
                    <div className="card-header"><h3>Result</h3></div>
                    <div className="card-body">
                        {response.error && <div className="alert alert-error">{response.error}</div>}
                        {response.detail && <div className="alert alert-error">{response.detail}</div>}
                        {response.status === 'ok' && (
                            <>
                                <div className="stats-grid">
                                    <div className="stat-card"><div className="stat-value">{response.protocols_accepted}</div><div className="stat-label">Protocols Accepted</div></div>
                                    <div className="stat-card"><div className="stat-value">{response.ptu2_files_loaded}</div><div className="stat-label">PTU2 Loaded</div></div>
                                    {response.tx_ant_diag_loaded > 0 && <div className="stat-card"><div className="stat-value">{response.tx_ant_diag_loaded}</div><div className="stat-label">TxAntDiag Loaded</div></div>}
                                </div>
                                {response.filters_applied && (
                                    <details style={{marginTop:'var(--space-4)',fontSize:'var(--text-sm)'}}>
                                        <summary style={{cursor:'pointer',color:'var(--color-text-muted)'}}>Filters Applied</summary>
                                        <pre style={{marginTop:8,padding:'var(--space-3)',background:'var(--color-surface-2)',borderRadius:'var(--radius)',overflow:'auto',fontSize:'var(--text-xs)'}}>{JSON.stringify(response.filters_applied,null,2)}</pre>
                                    </details>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
