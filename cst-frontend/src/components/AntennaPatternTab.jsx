import { useState } from 'react';

const API = 'http://localhost:8000';

const PATTERN_TYPES = { 1: 'TX-RX', 2: 'TX only', 3: 'RX only' };
const ROTATION_AXES = { 1: 'Z / Azimuth', 2: 'Y / Elevation' };
const GAIN_METHODS = { 1: 'Step-wise', 2: 'Interpolation' };
const OUTPUT_VERSIONS = { 0: 'JSON v1', 1: 'YAML v1', 2: 'YAML v2' };

const defaultTable = () => ({
    antenna_pattern_idx: 0,
    patternType: 1,
    rotationAxis: 1,
    nofApplicableTxAnt: 1,
    nofApplicableRxAnt: 4,
    applTxAntInd: [0],
    applRxAntInd: [0, 1, 2, 3],
    gainCalcMethod: 1,
});

export default function AntennaPatternTab() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [outputFiles, setOutputFiles] = useState([]);

    // Sensor muster
    const [useSensorMuster, setUseSensorMuster] = useState(0);
    const [sensorMusterList, setSensorMusterList] = useState('rf,dsp,PT,MA');

    // Chirp config
    const [chirp0, setChirp0] = useState(1);
    const [chirp1, setChirp1] = useState(0);
    const [chirp2, setChirp2] = useState(0);
    const [chirp3, setChirp3] = useState(0);

    // PTU2 input conf
    const [diagTypeInfo, setDiagTypeInfo] = useState(1);
    const [targetAngle, setTargetAngle] = useState(1);
    const [upsideDown, setUpsideDown] = useState(0);
    const [upsideDownInfo, setUpsideDownInfo] = useState(1);

    // Tables
    const [tables, setTables] = useState([
        { ...defaultTable(), antenna_pattern_idx: 0, rotationAxis: 1 },
        { ...defaultTable(), antenna_pattern_idx: 1, rotationAxis: 2 },
    ]);

    // Output
    const [outputVersion, setOutputVersion] = useState(0);
    const [headerName, setHeaderName] = useState('Antenna_Pattern_Tables');
    const [headerType, setHeaderType] = useState('antennaPattern');

    const updateTable = (idx, field, val) =>
        setTables(prev => prev.map((t, i) => i === idx ? { ...t, [field]: val } : t));

    const parseIndices = (str) => str.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));

    const handleStart = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch(`${API}/api/antenna_patterns/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    use_sensor_muster: useSensorMuster,
                    sensor_muster_list: useSensorMuster ? sensorMusterList.split(',').map(s => s.trim()) : [],
                    chirp_config: { chirp0, chirp1, chirp2, chirp3 },
                    ptu2_input_conf: {
                        diagTypeInfo, targetAngle, upsideDown, upsideDownInfo,
                        tables,
                    },
                    output_version: outputVersion,
                    header_name: headerName,
                    header_type: headerType,
                }),
            });
            const data = await res.json();
            setResult(data);

            if (data.status === 'success') {
                const filesRes = await fetch(`${API}/api/downloads/list/antenna_patterns/recursive`);
                const filesData = await filesRes.json();
                setOutputFiles(filesData.files ?? []);
            }
        } catch (err) {
            setResult({ error: err.message });
        }
        setLoading(false);
    };

    const DownloadIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>;
    const PlusIcon = () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>;
    const XIcon = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;

    return (
        <div style={{display:'flex',flexDirection:'column',gap:'var(--space-4)'}}>
        <div className="card">
            <div className="card-header"><h3>Antenna Patterns</h3></div>
            <div className="card-body" style={{display:'flex',flexDirection:'column',gap:'var(--space-5)'}}>

            <div className="section">
                <div className="section-label">Sensor Muster</div>
                <div className="check-group">
                    <label className="check-item"><input type="checkbox" checked={useSensorMuster === 1} onChange={e => setUseSensorMuster(e.target.checked ? 1 : 0)} /> Use Sensor Muster</label>
                </div>
                {useSensorMuster === 1 && (
                    <div className="form-group" style={{marginTop:'var(--space-2)'}}>
                        <label className="form-label">Sensor List (comma-separated)</label>
                        <input className="input" type="text" value={sensorMusterList} onChange={e => setSensorMusterList(e.target.value)} />
                    </div>
                )}
            </div>

            <div className="section">
                <div className="section-label">Chirps</div>
                <div className="check-group">
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

            <div className="section">
                <div className="section-label">PTU2 Input Configuration</div>
                <div className="check-group">
                <label><input type="checkbox" checked={diagTypeInfo === 1} onChange={e => setDiagTypeInfo(e.target.checked ? 1 : 0)} /> Diag Type Info in Files</label>
                <label><input type="checkbox" checked={targetAngle === 1} onChange={e => setTargetAngle(e.target.checked ? 1 : 0)} /> Target Angle</label>
                <label><input type="checkbox" checked={upsideDown === 1} onChange={e => setUpsideDown(e.target.checked ? 1 : 0)} /> Upside Down</label>
                <label className="check-item"><input type="checkbox" checked={upsideDownInfo === 1} onChange={e => setUpsideDownInfo(e.target.checked ? 1 : 0)} /> Upside Down Info in Files</label>
                </div>
            </div>

            <div className="section">
                <div className="section-label">Antenna Pattern Tables</div>
                <div className="antenna-table-editor">
                {tables.map((t, i) => (
                    <div key={i} className="antenna-table-card">
                        <div className="antenna-table-card-header">
                            <span>Table {i}</span>
                            <button className="btn btn-ghost" onClick={() => setTables(prev => prev.filter((_,j) => j !== i))} style={{padding:'2px 6px'}}><XIcon /></button>
                        </div>
                        <div className="check-group">
                        <label> Pattern Type:
                            <select value={t.patternType} onChange={e => updateTable(i, 'patternType', parseInt(e.target.value))}>
                                {Object.entries(PATTERN_TYPES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                            </select>
                        </label>
                        <label> Rotation:
                            <select value={t.rotationAxis} onChange={e => updateTable(i, 'rotationAxis', parseInt(e.target.value))}>
                                {Object.entries(ROTATION_AXES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                            </select>
                        </label>
                        <label> Gain Calc:
                            <select value={t.gainCalcMethod} onChange={e => updateTable(i, 'gainCalcMethod', parseInt(e.target.value))}>
                                {Object.entries(GAIN_METHODS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                            </select>
                        </label>
                        <label> #TX Ant: <input type="number" value={t.nofApplicableTxAnt} onChange={e => updateTable(i, 'nofApplicableTxAnt', parseInt(e.target.value))} style={{ width: 45 }} /></label>
                        <label> TX Indices: <input type="text" value={t.applTxAntInd.join(',')} onChange={e => updateTable(i, 'applTxAntInd', parseIndices(e.target.value))} style={{ width: 80 }} /></label>
                        <label> #RX Ant: <input type="number" value={t.nofApplicableRxAnt} onChange={e => updateTable(i, 'nofApplicableRxAnt', parseInt(e.target.value))} style={{ width: 45 }} /></label>
                        <label className="check-item"> RX Indices: <input className="input input-sm" type="text" value={t.applRxAntInd.join(',')} onChange={e => updateTable(i, 'applRxAntInd', parseIndices(e.target.value))} style={{ width: 80 }} /></label>
                        </div>
                    </div>
                ))}
                </div>{/* antenna-table-editor */}
                <button className="btn btn-secondary" style={{marginTop:'var(--space-2)'}} disabled={tables.length >= 8} onClick={() => setTables(prev => [...prev, { ...defaultTable(), antenna_pattern_idx: prev.length }])}><PlusIcon /> Add Table {tables.length >= 8 ? '(Max 8)' : ''}</button>
            </div>

            <div className="section">
                <div className="section-label">Output</div>
                <div className="row">
                    <div className="col">
                        <div className="form-group">
                            <label className="form-label">Format</label>
                            <select className="select-field" value={outputVersion} onChange={e => setOutputVersion(parseInt(e.target.value))}>
                                {Object.entries(OUTPUT_VERSIONS).map(([v,l]) => <option key={v} value={v}>{l}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="col">
                        <div className="form-group">
                            <label className="form-label">Header Name</label>
                            <input className="input" type="text" value={headerName} onChange={e => setHeaderName(e.target.value)} />
                        </div>
                    </div>
                    <div className="col">
                        <div className="form-group">
                            <label className="form-label">Header Type</label>
                            <input className="input" type="text" value={headerType} onChange={e => setHeaderType(e.target.value)} />
                        </div>
                    </div>
                </div>
            </div>

            </div>{/* card-body */}
            <div className="card-footer">
                <button className="btn btn-primary" onClick={handleStart} disabled={loading}>
                    {loading ? <><span className="spinner" /> Generating...</> : 'Generate Antenna Patterns'}
                </button>
                {outputFiles.length > 0 && <button className="btn btn-danger" onClick={async () => { await fetch(`${API}/api/downloads/clear/antenna_patterns`,{method:'DELETE'}); setOutputFiles([]); }}>Clear Output</button>}
            </div>
        </div>{/* card */}

            {result?.error && <div className="alert alert-error">{result.error}</div>}
            {result?.detail && <div className="alert alert-error">{result.detail}</div>}
            {result?.status === 'success' && <div className="alert alert-success">Antenna patterns generated</div>}

            {outputFiles.length > 0 && (
                <div className="card">
                    <div className="card-header"><h3>Output Files</h3></div>
                    <div className="card-body">
                        <ul className="output-file-list">
                            {outputFiles.map(f => (<li key={f.path}><a href={`${API}/api/downloads/download/antenna_patterns/${f.path}`} download><DownloadIcon />{f.path}</a><span style={{fontSize:'var(--text-xs)',color:'var(--color-text-muted)',marginLeft:'var(--space-2)'}}>{Math.round(f.size/1024)} KB</span></li>))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}
