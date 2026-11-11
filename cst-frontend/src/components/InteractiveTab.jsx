import { useEffect, useState } from 'react';
import { apiFetch, errorMessage } from '../api';

export default function InteractiveTab() {
    const [loading, setLoading] = useState(false);
    const [state, setState] = useState(null);

    const call = async (path, options) => {
        setLoading(true);
        try {
            const res = await apiFetch(path, options);
            if (!res.ok) { setState({ error: await errorMessage(res) }); return null; }
            return await res.json();
        } catch (err) {
            setState({ error: err.message });
            return null;
        } finally {
            setLoading(false);
        }
    };

    const handleFill = async () => {
        const data = await call('/api/interactive/fill', { method: 'POST' });
        if (data) setState(data);
    };

    const handleClear = async () => {
        if (await call('/api/interactive/clear', { method: 'DELETE' })) setState(null);
    };

    const handleGetState = async () => {
        const data = await call('/api/interactive/state');
        if (data) setState(data);
    };

    // The server keeps this session's fill result, so show it again after a reload
    useEffect(() => {
        let alive = true;
        apiFetch('/api/interactive/state')
            .then(res => (res.ok ? res.json() : null))
            .then(data => { if (alive && data) setState(data); })
            .catch(() => {});
        return () => { alive = false; };
    }, []);

    return (
        <div>
            <h3>Interactive</h3>
            <p>Loads available protocols and parameter combinations from parsed data. Actual chart rendering happens in the browser.</p>

            <button onClick={handleFill} disabled={loading}>{loading ? 'Loading...' : 'Fill / Refresh'}</button>
            <button onClick={handleGetState} disabled={loading}>Get State</button>
            <button onClick={handleClear} disabled={loading}>Clear</button>

            {state?.error && <p>Error: {state.error}</p>}

            {state?.filled && (
                <div>
                    <p>Protocols: <b>{state.protocol_count}</b> | Parameters: <b>{state.parameter_count}</b></p>

                    {state.protocols?.length > 0 && (
                        <div>
                            <h4>Protocols</h4>
                            <table border="1" cellPadding="4">
                                <thead><tr><th>Date/Time</th><th>Tuner</th><th>Sensor</th></tr></thead>
                                <tbody>
                                    {state.protocols.map((p, i) => (
                                        <tr key={i}>
                                            <td>{p.date_time}</td>
                                            <td>{p.tuner}</td>
                                            <td>{p.sensor}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {state.parameters?.length > 0 && (
                        <div>
                            <h4>Available Parameters ({state.parameters.length})</h4>
                            <table border="1" cellPadding="4">
                                <thead>
                                    <tr><th>Ant Type</th><th>Graph Type</th><th>Diagram</th><th>RX Ch</th></tr>
                                </thead>
                                <tbody>
                                    {state.parameters.slice(0, 100).map((p, i) => (
                                        <tr key={i}>
                                            <td>{p.antenna_type}</td>
                                            <td>{p.graph_type}</td>
                                            <td>{p.diagram_num}</td>
                                            <td>{p.rx_channel}</td>
                                        </tr>
                                    ))}
                                    {state.parameters.length > 100 && (
                                        <tr><td colSpan="4">... {state.parameters.length - 100} more rows</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
