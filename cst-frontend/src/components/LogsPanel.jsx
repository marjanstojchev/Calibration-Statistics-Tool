import { useState, useEffect, useRef } from 'react';
const API = 'http://localhost:8000';
const CHANNELS = [['system_diagrams','System Diagrams','system-diagrams'],['tx_diagrams','TX Diagrams','tx-diagrams'],['antenna_patterns','Ant. Patterns','antenna-patterns'],['main_load_data','Load Data','main-load-data']];
const PlayIcon = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>;
const StopIcon = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="18" height="18"/></svg>;
const TrashIcon = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>;
export default function LogsPanel() {
    const [active, setActive] = useState('system_diagrams');
    const [logs, setLogs] = useState({ system_diagrams:[], tx_diagrams:[], antenna_patterns:[], main_load_data:[] });
    const [streaming, setStreaming] = useState(false);
    const esRef = useRef(null);
    const logBoxRef = useRef(null);
    const startStream = (ch) => {
        if (esRef.current) esRef.current.close();
        const slug = CHANNELS.find(c=>c[0]===ch)?.[2] ?? ch.replace('_','-');
        const es = new EventSource(`${API}/api/logs/stream/${slug}`);
        es.onmessage = (e) => setLogs(prev => ({ ...prev, [ch]: [...prev[ch], e.data] }));
        es.onerror = () => es.close();
        esRef.current = es; setStreaming(true);
    };
    const stopStream = () => { esRef.current?.close(); esRef.current = null; setStreaming(false); };
    useEffect(() => { if (logBoxRef.current) logBoxRef.current.scrollTop = logBoxRef.current.scrollHeight; }, [logs]);
    useEffect(() => () => stopStream(), []);
    return (
        <div className="card">
            <div className="card-header"><h3>Logs</h3>
                <div className="btn-group">
                    <button className="btn btn-primary" onClick={() => startStream(active)} disabled={streaming}><PlayIcon /> Stream</button>
                    <button className="btn btn-secondary" onClick={stopStream} disabled={!streaming}><StopIcon /> Stop</button>
                    <button className="btn btn-ghost" onClick={() => setLogs(p=>({...p,[active]:[]}))}><TrashIcon /> Clear</button>
                </div>
            </div>
            <div className="card-body" style={{display:'flex',flexDirection:'column',gap:'var(--space-3)'}}>
                <div className="log-channel-tabs">
                    {CHANNELS.map(([k,l]) => <button key={k} className={`log-channel-btn ${active===k?'active':''}`} onClick={() => { setActive(k); if(streaming) startStream(k); }}>{l}</button>)}
                </div>
                <div ref={logBoxRef} className="log-viewer">
                    {logs[active].length === 0
                        ? <span style={{color:'#4a6080',fontStyle:'italic'}}># no logs — click Stream to start</span>
                        : logs[active].map((line,i) => <div key={i} className="log-entry">{line}</div>)}
                </div>
                <div style={{fontSize:'var(--text-xs)',color:'var(--color-text-faint)',display:'flex',gap:'var(--space-4)'}}>
                    <span>{logs[active].length} lines</span>
                    {streaming && <span style={{color:'var(--color-success)'}}>● Live</span>}
                </div>
            </div>
        </div>
    );
}
