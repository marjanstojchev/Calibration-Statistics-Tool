import { useState } from 'react';

const API = 'http://localhost:8000';

export default function HuellkurvenTab() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [outputFiles, setOutputFiles] = useState([]);

    // Data conf
    const [azDiag, setAzDiag] = useState(1);
    const [elDiag, setElDiag] = useState(1);
    const [minSigma, setMinSigma] = useState(-10);
    const [maxSigma, setMaxSigma] = useState(10);
    const [patternLimitsMethod, setPatternLimitsMethod] = useState(0);

    // Plot setup
    const [xScaleAuto, setXScaleAuto] = useState(0);
    const [xScaleAz, setXScaleAz] = useState(90.0);
    const [xScaleEl, setXScaleEl] = useState(45.0);

    // Chirp config
    const [chirp0, setChirp0] = useState(1);
    const [chirp1, setChirp1] = useState(0);
    const [chirp2, setChirp2] = useState(0);
    const [chirp3, setChirp3] = useState(0);

    const handleStart = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch(`${API}/api/huellkurven/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data_conf: { azDiag: azDiag, elDiag: elDiag, minSigma, maxSigma, patternLimitsMethod },
                    plot_setup: { xScaleSizeAuto: xScaleAuto, xScaleSizeAz: xScaleAz, xScaleSizeEl: xScaleEl },
                    chirp_config: { chirp0, chirp1, chirp2, chirp3 },
                }),
            });
            const data = await res.json();
            setResult(data);

            if (data.status === 'success') {
                const filesRes = await fetch(`${API}/api/downloads/list/huellkurven`);
                const filesData = await filesRes.json();
                setOutputFiles(filesData.files ?? []);
            }
        } catch (err) {
            setResult({ error: err.message });
        }
        setLoading(false);
    };

    const DownloadIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>;

    return (
        <div style={{display:'flex',flexDirection:'column',gap:'var(--space-4)'}}>
        <div className="card">
            <div className="card-header"><h3>Hüllkurven (Envelope Limits)</h3></div>
            <div className="card-body" style={{display:'flex',flexDirection:'column',gap:'var(--space-5)'}}>

            <div className="section">
                <div className="section-label">Diagrams</div>
                <div className="check-group">
                    <label className="check-item"><input type="checkbox" checked={azDiag === 1} onChange={e => setAzDiag(e.target.checked ? 1 : 0)} /> Azimuth Diagrams</label>
                    <label className="check-item"><input type="checkbox" checked={elDiag === 1} onChange={e => setElDiag(e.target.checked ? 1 : 0)} /> Elevation Diagrams</label>
                </div>
            </div>

            <div className="section">
                <div className="section-label">Pattern Limits Method</div>
                <div className="radio-group">
                    <label className="radio-item"><input type="radio" name="plm" value={0} checked={patternLimitsMethod === 0} onChange={() => setPatternLimitsMethod(0)} /> Sigma-based</label>
                    <label className="radio-item"><input type="radio" name="plm" value={1} checked={patternLimitsMethod === 1} onChange={() => setPatternLimitsMethod(1)} /> Min/Max-based</label>
                </div>
                {patternLimitsMethod === 0 && (
                    <div className="check-group" style={{marginTop:'var(--space-2)'}}>
                        <label className="check-item">Min Sigma: <input className="input input-sm" type="number" value={minSigma} onChange={e => setMinSigma(parseInt(e.target.value))} style={{ width: 60 }} /></label>
                        <label className="check-item">Max Sigma: <input className="input input-sm" type="number" value={maxSigma} onChange={e => setMaxSigma(parseInt(e.target.value))} style={{ width: 60 }} /></label>
                    </div>
                )}
            </div>

            <div className="section">
                <div className="section-label">X-Scale</div>
                <div className="check-group">
                    <label className="check-item">X-Scale Auto<input type="checkbox" checked={xScaleAuto === 1} onChange={e => setXScaleAuto(e.target.checked ? 1 : 0)} /></label>
                    {xScaleAuto === 0 && (
                        <>
                            <label className="check-item">Az: <input className="input input-sm" type="number" value={xScaleAz} onChange={e => setXScaleAz(parseFloat(e.target.value))} style={{ width: 60 }} /></label>
                            <label className="check-item">El: <input className="input input-sm" type="number" value={xScaleEl} onChange={e => setXScaleEl(parseFloat(e.target.value))} style={{ width: 60 }} /></label>
                        </>
                    )}
                </div>
            </div>

            <div className="section">
                <div className="section-label">Chirps</div>
                <div className="check-group">
                <span>Chirps: </span>
                {[0,1,2,3].map(i => (
                    <label key={i}>
                        <input type="checkbox"
                            checked={[chirp0, chirp1, chirp2, chirp3][i] === 1}
                            onChange={e => [setChirp0,setChirp1,setChirp2,setChirp3][i](e.target.checked ? 1 : 0)} />
                        Chirp {i}
                    </label>
                ))}
                </div>
            </div>

            </div>{/* card-body */}
            <div className="card-footer">
                <button className="btn btn-primary" onClick={handleStart} disabled={loading}>
                    {loading ? <><span className="spinner" /> Computing...</> : 'Compute Hüllkurven'}
                </button>
                {outputFiles.length > 0 && <button className="btn btn-danger" onClick={async () => { await fetch(`${API}/api/downloads/clear/huellkurven`,{method:'DELETE'}); setOutputFiles([]); }}>Clear Output</button>}
            </div>
        </div>{/* card */}

            {result?.error && <div className="alert alert-error">{result.error}</div>}
            {result?.detail && <div className="alert alert-error">{result.detail}</div>}
            {result?.status === 'success' && <div className="alert alert-success">Hüllkurven computed successfully</div>}

            {outputFiles.length > 0 && (
                <div className="card">
                    <div className="card-header"><h3>Output Files</h3></div>
                    <div className="card-body">
                        <ul className="output-file-list">
                            {outputFiles.map(f => (<li key={f.path}><a href={`${API}/api/downloads/download/huellkurven/${f.path}`} download><DownloadIcon />{f.path}</a><span style={{fontSize:'var(--text-xs)',color:'var(--color-text-muted)',marginLeft:'var(--space-2)'}}>{Math.round(f.size/1024)} KB</span></li>))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}
