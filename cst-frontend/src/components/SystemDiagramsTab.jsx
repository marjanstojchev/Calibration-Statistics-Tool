import { useState } from 'react';

const API = 'http://localhost:8000';

const GRAPH_TYPES = ['level','avgLevel','normLevel','avgNormLevel','phaseDiff','avgPhaseDiff','diffPhaseDiff','avgDiffPhaseDiff','corrPhaseDiff','diffPhDiffIdealCurve'];

export default function SystemDiagramsTab() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [outputFiles, setOutputFiles] = useState([]);

    const [pptxTitle, setPptxTitle] = useState('Antenna_diagrams.pptx');

    // Plot setup
    const [targetAngle, setTargetAngle] = useState(1);
    const [upsideDown, setUpsideDown] = useState(0);
    const [xScaleAuto, setXScaleAuto] = useState(0);
    const [xScaleAz, setXScaleAz] = useState(90.0);
    const [xScaleEl, setXScaleEl] = useState(45.0);
    const [imageDpi, setImageDpi] = useState(220);
    const [allOnOneSlide, setAllOnOneSlide] = useState(1);
    const [separateRxCh, setSeparateRxCh] = useState(1);
    const [threeGraphLayout, setThreeGraphLayout] = useState(1);
    const [idealPhaseDiff, setIdealPhaseDiff] = useState(1);
    const [yLimitsAntTypeSeparately, setYLimitsAntTypeSeparately] = useState(1);
    const [sortByMeasAngle, setSortByMeasAngle] = useState(0);
    const [diffPhaseDiffScalingFactor, setDiffPhaseDiffScalingFactor] = useState(1.5);
    const [nofSensorMeasToShow, setNofSensorMeasToShow] = useState(32);
    const [imageGenerationMode, setImageGenerationMode] = useState(0); // 0=Rx-Channel, 1=Diagram Number

    // Diagram config
    const [selectDiagrams, setSelectDiagrams] = useState(0); // 0=all, 1=range, 2=list
    const [oddOrEven, setOddOrEven] = useState(0);
    const [lowerNumber, setLowerNumber] = useState(0);
    const [higherNumber, setHigherNumber] = useState(4);
    const [desiredList, setDesiredList] = useState('1,2,3,4');

    // Chirp config
    const [chirp0, setChirp0] = useState(1);
    const [chirp1, setChirp1] = useState(0);
    const [chirp2, setChirp2] = useState(0);
    const [chirp3, setChirp3] = useState(0);

    // Graph config (all fields)
    const [graphConfig, setGraphConfig] = useState({
        level: 1, avgLevel: 0, normLevel: 1, avgNormLevel: 0,
        phaseDiff: 1, avgPhaseDiff: 0, diffPhaseDiff: 0, avgDiffPhaseDiff: 0,
        corrPhaseDiff: 1, diffPhDiffIdealCurve: 1,
    });
    const toggleGraph = (key) => setGraphConfig(prev => ({ ...prev, [key]: prev[key] ? 0 : 1 }));

    // Two-graph: each config = one slide comparing 2 curves (primGraph vs secGraph)
    const [twoGraphConfigs, setTwoGraphConfigs] = useState([
        { enabled: false, primGraph: 'level', secGraph: 'normLevel' },
        { enabled: false, primGraph: 'corrPhaseDiff', secGraph: 'diffPhaseDiff' },
    ]);
    // Three-graph: each slot = one curve on the shared 3-graph slide
    const [threeGraphSlots, setThreeGraphSlots] = useState([
        { enabled: true, graphType: 'corrPhaseDiff' },
        { enabled: true, graphType: 'diffPhaseDiff' },
        { enabled: false, graphType: 'diffPhaseDiff' },
    ]);
    // Four-graph: each slot = one curve on the shared 4-graph slide
    const [fourGraphSlots, setFourGraphSlots] = useState([
        { enabled: true, graphType: 'level' },
        { enabled: false, graphType: 'corrPhaseDiff' },
        { enabled: false, graphType: 'diffPhaseDiff' },
    ]);
    // All-on-one: one slide with individual graph toggles
    const [allOnOneEnabled, setAllOnOneEnabled] = useState(true);
    const [allOnOneGraphs, setAllOnOneGraphs] = useState([
        { enabled: true, graphType: 'level' },
        { enabled: true, graphType: 'corrPhaseDiff' },
        { enabled: true, graphType: 'diffPhaseDiff' },
    ]);

    

    const handleStart = async () => {
        setLoading(true);
        setResult(null);
        try {
            // Parse diagram config list if "Desired list" mode is selected
            const diagramConfigList = selectDiagrams === 2 
                ? desiredList.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
                : [];
            
            const res = await fetch(`${API}/api/system_diagrams/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pptx_title: pptxTitle,
                    plot_setup: {
                        targetAngle, upsideDown,
                        xScaleSizeAuto: xScaleAuto,
                        xScaleSizeAz: xScaleAz,
                        xScaleSizeEl: xScaleEl,
                        imageDpi, allOnOneSlide,
                        SeparateRxCh: separateRxCh,
                        threeGraphLayout,
                        idealPhaseDiff,
                        yLimitsAntTypeSeparately,
                        sortByMeasAngle,
                        diffPhaseDiffScalingFactor,
                        nofSensorMeasToShow,
                        graphsPerSlide: imageGenerationMode,
                    },
                    chirp_config: { chirp0, chirp1, chirp2, chirp3 },
                    graph_config: graphConfig,
                    diagram_config: { selectDiagrams, oddOrEven, lowerNumber, higherNumber },
                    diagram_config_list: diagramConfigList,
                    two_graph_setup_list: twoGraphConfigs.filter(c => c.enabled).map(c => ({ primGraph: c.primGraph, secGraph: c.secGraph })),
                    three_graph_setup_list: threeGraphSlots.filter(s => s.enabled).map(s => ({ graphType: s.graphType })),
                    four_graph_setup_list: fourGraphSlots.filter(s => s.enabled).map(s => ({ graphType: s.graphType })),
                    all_on_one_slide_graph_list: allOnOneEnabled ? allOnOneGraphs.filter(g => g.enabled).map(g => ({ graphType: g.graphType })) : [],
                }),
            });
            const data = await res.json();
            setResult(data);

            if (data.status === 'success') {
                const filesRes = await fetch(`${API}/api/downloads/list/system_diagrams`);
                const filesData = await filesRes.json();
                setOutputFiles(filesData.files ?? []);
            }
        } catch (err) {
            setResult({ error: err.message });
        }
        setLoading(false);
    };

    const updateTwoGraphConfig = (idx, field, val) =>
        setTwoGraphConfigs(prev => prev.map((item, i) => i === idx ? { ...item, [field]: val } : item));
    const updateThreeGraphSlot = (idx, field, val) =>
        setThreeGraphSlots(prev => prev.map((item, i) => i === idx ? { ...item, [field]: val } : item));
    const updateFourGraphSlot = (idx, field, val) =>
        setFourGraphSlots(prev => prev.map((item, i) => i === idx ? { ...item, [field]: val } : item));
    const updateAllOnOneGraph = (idx, field, val) =>
        setAllOnOneGraphs(prev => prev.map((item, i) => i === idx ? { ...item, [field]: val } : item));

    const DownloadIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>;

    // Slide layout SVG previews
    const SlidePreview2 = () => (<svg viewBox="0 0 48 32" style={{width:'100%',height:'100%'}}><rect x="1" y="1" width="22" height="30" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><rect x="25" y="1" width="22" height="30" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><line x1="3" y1="28" x2="21" y2="10" stroke="var(--color-primary)" strokeWidth="1" opacity="0.7"/><line x1="27" y1="28" x2="45" y2="10" stroke="var(--color-success)" strokeWidth="1" opacity="0.7"/></svg>);
    const SlidePreview3 = () => (<svg viewBox="0 0 48 32" style={{width:'100%',height:'100%'}}><rect x="1" y="1" width="14" height="30" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><rect x="17" y="1" width="14" height="30" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><rect x="33" y="1" width="14" height="30" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/></svg>);
    const SlidePreview4 = () => (<svg viewBox="0 0 48 32" style={{width:'100%',height:'100%'}}><rect x="1" y="1" width="22" height="14" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><rect x="25" y="1" width="22" height="14" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><rect x="1" y="17" width="22" height="14" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><rect x="25" y="17" width="22" height="14" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/></svg>);
    const SlidePreviewAll = () => (<svg viewBox="0 0 48 32" style={{width:'100%',height:'100%'}}><rect x="1" y="1" width="46" height="30" rx="1" fill="none" stroke="var(--color-border)" strokeWidth="1.5"/><line x1="3" y1="27" x2="45" y2="8" stroke="var(--color-primary)" strokeWidth="1" opacity="0.5"/><line x1="3" y1="22" x2="45" y2="14" stroke="var(--color-success)" strokeWidth="1" opacity="0.5"/></svg>);

    return (
        <div style={{display:'flex',flexDirection:'column',gap:'var(--space-4)'}}>
            <div className="card">
            <div className="card-header"><h3>System Diagrams</h3></div>
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
                <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--space-4)'}}>
                    {/* Left Column */}
                    <div style={{display:'flex',flexDirection:'column',gap:'var(--space-3)'}}>
                        <div>
                            <div style={{fontWeight:500,marginBottom:'var(--space-1)'}}>Script Mode</div>
                            <label><input type="radio" name="scriptMode" checked disabled /> Presentation</label>
                        </div>
                        
                        <div>
                            <div style={{fontWeight:500,marginBottom:'var(--space-1)'}}>Image Generation Mode</div>
                            <label><input type="radio" name="imgGenMode" checked={imageGenerationMode === 0} onChange={() => setImageGenerationMode(0)} /> Rx-Channel</label>
                            <label><input type="radio" name="imgGenMode" checked={imageGenerationMode === 1} onChange={() => setImageGenerationMode(1)} /> Diagram Number</label>
                        </div>
                        
                        <label><input type="checkbox" checked={threeGraphLayout === 1} onChange={e => setThreeGraphLayout(e.target.checked ? 1 : 0)} /> 3-Graph Layout Images</label>
                        
                        <div>
                            <div style={{fontWeight:500,marginBottom:'var(--space-1)'}}>Image DPI:</div>
                            <input type="number" className='plotSetup' id='dpi' value={imageDpi} onChange={e => { const val = parseInt(e.target.value); setImageDpi(val > 600 ? 600 : val < 72 ? 72 : val); }} min="72" max="600" style={{ width: 100 }} />
                        </div>
                    </div>
                    
                    {/* Right Column */}
                    <div style={{display:'flex',flexDirection:'column',gap:'var(--space-2)'}}>
                        <label><input type="checkbox" checked={xScaleAuto === 1} onChange={e => setXScaleAuto(e.target.checked ? 1 : 0)} /> X-Scale Autoscale</label>
                        
                        {xScaleAuto === 0 && (
                            <div style={{marginLeft:'var(--space-4)',marginBottom:'var(--space-2)'}}>
                                <label style={{display:'block',marginBottom:'var(--space-1)'}}>X-Scale Azimuth: <input className="plotSetup" id='az' type="number" value={xScaleAz} onChange={e => { const val = parseFloat(e.target.value); setXScaleAz(val > 90 ? 90 : val < 0 ? 0 : val); }} min="0" max="90" style={{ width: 70 }} /></label>
                                <label style={{display:'block'}}>X-Scale Elevation: <input className="plotSetup" id='el' type="number" value={xScaleEl} onChange={e => { const val = parseFloat(e.target.value); setXScaleEl(val > 150 ? 150 : val < 0 ? 0 : val); }} min="0" max="150" style={{ width: 70 }} /></label>
                            </div>
                        )}
                        
                        <div style={{fontWeight:500,marginTop:'var(--space-2)',marginBottom:'var(--space-1)'}}>Y-Limits Yield</div>
                        <label><input type="radio" name="yLimits" checked={yLimitsAntTypeSeparately === 1} onChange={() => setYLimitsAntTypeSeparately(1)} /> Per Antenna-Type</label>
                        <label><input type="radio" name="yLimits" checked={yLimitsAntTypeSeparately === 0} onChange={() => setYLimitsAntTypeSeparately(0)} /> All Antenna-Types</label>
                        
                        <label style={{marginTop:'var(--space-2)'}}><input type="checkbox" checked={targetAngle === 1} onChange={e => setTargetAngle(e.target.checked ? 1 : 0)} /> Target Angle</label>
                        <label><input type="checkbox" checked={upsideDown === 1} onChange={e => setUpsideDown(e.target.checked ? 1 : 0)} /> Upside Down</label>
                        <label><input type="checkbox" checked={idealPhaseDiff === 1} onChange={e => setIdealPhaseDiff(e.target.checked ? 1 : 0)} /> Ideal Phase Diff</label>
                        <label><input type="checkbox" checked={separateRxCh === 1} onChange={e => setSeparateRxCh(e.target.checked ? 1 : 0)} /> Separate RX Channels</label>
                        <label><input type="checkbox" checked={allOnOneSlide === 1} onChange={e => setAllOnOneSlide(e.target.checked ? 1 : 0)} /> All on One Slide</label>
                        <label><input type="checkbox" checked={sortByMeasAngle === 1} onChange={e => setSortByMeasAngle(e.target.checked ? 1 : 0)} /> Sort by Meas. Angle</label>
                        
                        <label style={{marginTop:'var(--space-3)'}}>
                            <span style={{display:'inline-block',marginBottom:'var(--space-1)'}}>Diff. Phase Diff. Scaling Factor:</span><br/>
                            <input type="number" step="0.1" value={diffPhaseDiffScalingFactor} onChange={e => setDiffPhaseDiffScalingFactor(parseFloat(e.target.value))} style={{ width: 70 }} />
                        </label>
                    </div>
                </div>
            </div>

            <div className="section">
                <div className="section-label">Diagram Configuration</div>
                <div style={{display:'flex',gap:'var(--space-5)',flexWrap:'wrap'}}>
                    {/* Input Mode */}
                    <div style={{minWidth:150}}>
                        <div style={{fontWeight:500,marginBottom:'var(--space-2)'}}>Input Mode</div>
                        <div style={{display:'flex',flexDirection:'column',gap:'var(--space-1)'}}>
                            <label><input type="radio" name="selDiag" value={0} checked={selectDiagrams === 0} onChange={() => setSelectDiagrams(0)} /> All</label>
                            <label><input type="radio" name="selDiag" value={1} checked={selectDiagrams === 1} onChange={() => setSelectDiagrams(1)} /> Desired range</label>
                            <label><input type="radio" name="selDiag" value={2} checked={selectDiagrams === 2} onChange={() => setSelectDiagrams(2)} /> Desired list</label>
                        </div>
                        {selectDiagrams === 2 && (
                            <input type="text" value={desiredList} onChange={e => setDesiredList(e.target.value)} placeholder="1,2,3,4" style={{marginTop:'var(--space-2)',width:'100%',maxWidth:140}} />
                        )}
                    </div>
                    
                    {/* Desired Range (only show if range selected) */}
                    {selectDiagrams === 1 && (
                        <div style={{minWidth:180}}>
                            <div style={{fontWeight:500,marginBottom:'var(--space-2)'}}>Desired Range</div>
                            <div style={{display:'flex',flexDirection:'column',gap:'var(--space-2)'}}>
                                <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)'}}>
                                    Low: <input type="number" value={lowerNumber} onChange={e => setLowerNumber(parseInt(e.target.value))} style={{ width: 80 }} />
                                </label>
                                <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)'}}>
                                    High: <input type="number" value={higherNumber} onChange={e => setHigherNumber(parseInt(e.target.value))} style={{ width: 80 }} />
                                </label>
                            </div>
                        </div>
                    )}
                    
                    {/* Odd / Even */}
                    <div style={{minWidth:150}}>
                        <div style={{fontWeight:500,marginBottom:'var(--space-2)'}}>Odd / Even</div>
                        <div style={{display:'flex',flexDirection:'column',gap:'var(--space-1)'}}>
                            <label><input type="radio" name="oddEven" value={0} checked={oddOrEven === 0} onChange={() => setOddOrEven(0)} /> Both</label>
                            <label><input type="radio" name="oddEven" value={1} checked={oddOrEven === 1} onChange={() => setOddOrEven(1)} /> Odd</label>
                            <label><input type="radio" name="oddEven" value={2} checked={oddOrEven === 2} onChange={() => setOddOrEven(2)} /> Even</label>
                        </div>
                    </div>
                </div>
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
                <div className="section-label">Graph Types</div>
                <div className="check-group">
                {GRAPH_TYPES.map(g => (
                    <label key={g}>
                        <input type="checkbox" checked={graphConfig[g] === 1} onChange={() => toggleGraph(g)} />
                        {g}
                    </label>
                ))}
                </div>
            </div>

            <div className="section">
                <div className="section-label">Slide Configuration</div>
                <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr 1fr',gap:'var(--space-4)'}}>

                {/* Two-Graph: each config = one slide comparing 2 curves */}
                <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                <div style={{fontWeight:600,fontSize:'var(--text-sm)',marginBottom:'var(--space-2)',display:'flex',alignItems:'center',justifyContent:'center',gap:'var(--space-2)'}}><div className="slide-preview"><SlidePreview2 /></div>Two - Graph Layout</div>
                {twoGraphConfigs.map((config, i) => (
                    <div key={i} style={{marginBottom:'var(--space-2)'}}>
                        <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)',color:'var(--color-primary)',marginBottom:'var(--space-1)'}}>
                            <input type="checkbox" checked={config.enabled} onChange={e => updateTwoGraphConfig(i, 'enabled', e.target.checked)} />
                            Configuration {i + 1}
                        </label>
                        <select id={`primGraph-${i}`} value={config.primGraph} onChange={e => updateTwoGraphConfig(i, 'primGraph', e.target.value)} style={{display:'block',width:'100%',marginBottom:'var(--space-1)'}}>
                            {GRAPH_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                        <select id={`secGraph-${i}`} value={config.secGraph} onChange={e => updateTwoGraphConfig(i, 'secGraph', e.target.value)} style={{display:'block',width:'100%'}}>
                            {GRAPH_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                    </div>
                ))}
                </div>

                {/* Four-Graph: each slot = one curve on the 4-graph slide */}
                <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                <div style={{fontWeight:600,fontSize:'var(--text-sm)',marginBottom:'var(--space-2)',display:'flex',alignItems:'center',justifyContent:'center',gap:'var(--space-2)'}}><div className="slide-preview"><SlidePreview4 /></div>Four-Graph Layout</div>
                {fourGraphSlots.map((slot, i) => (
                    <div key={i} style={{marginBottom:'var(--space-2)'}}>
                        <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)',color:'var(--color-primary)',marginBottom:'var(--space-1)'}}>
                            <input type="checkbox" checked={slot.enabled} onChange={e => updateFourGraphSlot(i, 'enabled', e.target.checked)} />
                            Configuration {i + 1}
                        </label>
                        <select value={slot.graphType} onChange={e => updateFourGraphSlot(i, 'graphType', e.target.value)} style={{display:'block',width:'100%'}}>
                            {GRAPH_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                    </div>
                ))}
                </div>

                {/* Three-Graph: each slot = one curve on the 3-graph slide */}
                <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                <div style={{fontWeight:600,fontSize:'var(--text-sm)',marginBottom:'var(--space-2)',display:'flex',alignItems:'center',justifyContent:'center',gap:'var(--space-2)'}}><div className="slide-preview"><SlidePreview3 /></div>Three-Graph Layout</div>
                {threeGraphSlots.map((slot, i) => (
                    <div key={i} style={{marginBottom:'var(--space-2)'}}>
                        <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)',color:'var(--color-primary)',marginBottom:'var(--space-1)'}}>
                            <input type="checkbox" checked={slot.enabled} onChange={e => updateThreeGraphSlot(i, 'enabled', e.target.checked)} />
                            Configuration {i + 1}
                        </label>
                        <select value={slot.graphType} onChange={e => updateThreeGraphSlot(i, 'graphType', e.target.value)} style={{display:'block',width:'100%'}}>
                            {GRAPH_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                    </div>
                ))}
                </div>

                {/* All-on-one: one slide, individual graph toggles */}
                <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                <div style={{fontWeight:600,fontSize:'var(--text-sm)',marginBottom:'var(--space-2)',display:'flex',alignItems:'center',justifyContent:'center',gap:'var(--space-2)'}}><div className="slide-preview"><SlidePreviewAll /></div>
                    <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)',color:'var(--color-primary)'}}>
                        <input type="checkbox" checked={allOnOneEnabled} onChange={e => setAllOnOneEnabled(e.target.checked)} />
                        All-Graphs Slide
                    </label>
                </div>
                <div style={{marginBottom:'var(--space-2)',fontSize:'var(--text-sm)'}}>Sensor Slide:</div>
                <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)',marginBottom:'var(--space-3)',fontSize:'var(--text-sm)'}}>
                    Num. of Sensors:
                    <input type="number" value={nofSensorMeasToShow} onChange={e => setNofSensorMeasToShow(parseInt(e.target.value))} disabled={!allOnOneEnabled} style={{width:60,marginLeft:'var(--space-2)'}} />
                </label>
                {allOnOneGraphs.map((graph, i) => (
                    <div key={i} style={{marginBottom:'var(--space-2)'}}>
                        <label style={{display:'flex',alignItems:'center',gap:'var(--space-2)',color:'var(--color-primary)',marginBottom:'var(--space-1)'}}>
                            <input type="checkbox" checked={graph.enabled} onChange={e => updateAllOnOneGraph(i, 'enabled', e.target.checked)} disabled={!allOnOneEnabled} />
                            Graph {i + 1}
                        </label>
                        <select value={graph.graphType} onChange={e => updateAllOnOneGraph(i, 'graphType', e.target.value)} disabled={!allOnOneEnabled || !graph.enabled} style={{display:'block',width:'100%'}}>
                            {GRAPH_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                    </div>
                ))}
                </div>

                </div>{/* end grid */}
            </div>

            </div>{/* card-body */}
            <div className="card-footer">
                <button className="btn btn-primary" onClick={handleStart} disabled={loading}>
                    {loading ? <><span className="spinner" /> Generating...</> : 'Generate PPTX'}
                </button>
                {outputFiles.length > 0 && <button className="btn btn-danger" onClick={async () => { await fetch(`${API}/api/downloads/clear/system_diagrams`,{method:'DELETE'}); setOutputFiles([]); }}>Clear Output</button>}
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
                            {outputFiles.map(f => (
                                <li key={f}><a href={`${API}/api/downloads/download/system_diagrams/${f}`} download><DownloadIcon /> {f}</a></li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}
