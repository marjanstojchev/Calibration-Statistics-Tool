import { useState } from 'react';

const API = 'http://localhost:8000';

export default function TxDiagramsTab() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [outputFiles, setOutputFiles] = useState([]);
    const [pptxTitle, setPptxTitle] = useState('TxAntenna_diagrams.pptx');

    // Plot setup
    const [targetAngle, setTargetAngle] = useState(0);
    const [upsideDown, setUpsideDown] = useState(0);
    const [azDiag, setAzDiag] = useState(1);
    const [elDiag, setElDiag] = useState(1);
    const [xScaleAuto, setXScaleAuto] = useState(0);
    const [xScaleAz, setXScaleAz] = useState(90.0);
    const [xScaleEl, setXScaleEl] = useState(45.0);
    const [imageDpi, setImageDpi] = useState(220);
    const [plotOrigGraphs, setPlotOrigGraphs] = useState(1);
    const [plotNormGraphs, setPlotNormGraphs] = useState(1);

    // Graph config
    const [showLevel, setShowLevel] = useState(1);
    const [showLevelPowMet, setShowLevelPowMet] = useState(0);
    const [showFrequency, setShowFrequency] = useState(0);
    const [showTime, setShowTime] = useState(0);

    const handleStart = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch(`${API}/api/tx_diagrams/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pptx_title: pptxTitle,
                    plot_setup: {
                        targetAngle, upsideDown,
                        AzDiag: azDiag, ElDiag: elDiag,
                        xScaleSizeAuto: xScaleAuto,
                        xScaleSizeAz: xScaleAz,
                        xScaleSizeEl: xScaleEl,
                        imageDpi,
                        plotOrigGraphs, plotNormGraphs,
                    },
                    graph_config: {
                        level: showLevel,
                        levelPowMet: showLevelPowMet,
                        frequency: showFrequency,
                        time: showTime,
                    },
                }),
            });
            const data = await res.json();
            setResult(data);

            if (data.status === 'success') {
                const filesRes = await fetch(`${API}/api/downloads/list/tx_diagrams`);
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
            <div className="card-header"><h3>TX Antenna Diagrams</h3></div>
            <div className="card-body" style={{display:'flex',flexDirection:'column',gap:'var(--space-5)'}}>

            <div className="section">
                <div className="section-label">Output</div>
                <div className="form-group">
                    <label className="form-label">PPTX File Name</label>
                    <input className="input" type="text" value={pptxTitle} onChange={e => setPptxTitle(e.target.value)} />
                </div>
            </div>

            <div className="section">
                <div className="section-label">Plot Setup</div>
                <div className="check-group">
                <label><input type="checkbox" checked={targetAngle === 1} onChange={e => setTargetAngle(e.target.checked ? 1 : 0)} /> Target Angle</label>
                <label><input type="checkbox" checked={upsideDown === 1} onChange={e => setUpsideDown(e.target.checked ? 1 : 0)} /> Upside Down</label>
                <label><input type="checkbox" checked={azDiag === 1} onChange={e => setAzDiag(e.target.checked ? 1 : 0)} /> Azimuth Diagrams</label>
                <label><input type="checkbox" checked={elDiag === 1} onChange={e => setElDiag(e.target.checked ? 1 : 0)} /> Elevation Diagrams</label>
                <label><input type="checkbox" checked={plotOrigGraphs === 1} onChange={e => setPlotOrigGraphs(e.target.checked ? 1 : 0)} /> Original Graphs</label>
                <label><input type="checkbox" checked={plotNormGraphs === 1} onChange={e => setPlotNormGraphs(e.target.checked ? 1 : 0)} /> Normalised Graphs</label>
                <label>X-Scale Auto<input type="checkbox" checked={xScaleAuto === 1} onChange={e => setXScaleAuto(e.target.checked ? 1 : 0)} /></label>
                {xScaleAuto === 0 && (
                    <>
                        <label>Az: <input type="number" value={xScaleAz} onChange={e => setXScaleAz(parseFloat(e.target.value))} style={{ width: 60 }} /></label>
                        <label>El: <input type="number" value={xScaleEl} onChange={e => setXScaleEl(parseFloat(e.target.value))} style={{ width: 60 }} /></label>
                    </>
                )}
                <label className="check-item">DPI: <input className="input input-sm" type="number" value={imageDpi} onChange={e => setImageDpi(parseInt(e.target.value))} style={{ width: 60 }} /></label>
                </div>
            </div>

            <div className="section">
                <div className="section-label">Show Graphs</div>
                <div className="check-group">
                <label><input type="checkbox" checked={showLevel === 1} onChange={e => setShowLevel(e.target.checked ? 1 : 0)} /> Level (Spectrum)</label>
                <label><input type="checkbox" checked={showLevelPowMet === 1} onChange={e => setShowLevelPowMet(e.target.checked ? 1 : 0)} /> Level (Power Meter)</label>
                <label><input type="checkbox" checked={showFrequency === 1} onChange={e => setShowFrequency(e.target.checked ? 1 : 0)} /> Frequency</label>
                <label className="check-item"><input type="checkbox" checked={showTime === 1} onChange={e => setShowTime(e.target.checked ? 1 : 0)} /> Time</label>
                </div>
            </div>

            </div>{/* card-body */}
            <div className="card-footer">
                <button className="btn btn-primary" onClick={handleStart} disabled={loading}>
                    {loading ? <><span className="spinner" /> Generating...</> : 'Generate PPTX'}
                </button>
                {outputFiles.length > 0 && <button className="btn btn-danger" onClick={async () => { await fetch(`${API}/api/downloads/clear/tx_diagrams`,{method:'DELETE'}); setOutputFiles([]); }}>Clear Output</button>}
            </div>
        </div>{/* card */}

            {result?.error && <div className="alert alert-error">{result.error}</div>}
            {result?.detail && <div className="alert alert-error">{result.detail}</div>}
            {result?.status === 'success' && <div className="alert alert-success">Done: {result.output_path}</div>}

            {outputFiles.length > 0 && (
                <div className="card">
                    <div className="card-header"><h3>Output Files</h3></div>
                    <div className="card-body">
                        <ul className="output-file-list">
                            {outputFiles.map(f => (<li key={f}><a href={`${API}/api/downloads/download/tx_diagrams/${f}`} download><DownloadIcon />{f}</a></li>))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}
