import { useState } from 'react';

const API = 'http://localhost:8000';

export default function InteractiveTab() {
    const [loading, setLoading] = useState(false);
    const [state, setState] = useState(null);

    const handleFill = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API}/api/interactive/fill`, { method: 'POST' });
            const data = await res.json();
            setState(data);
        } catch (err) {
            setState({ error: err.message });
        }
        setLoading(false);
    };

    const handleClear = async () => {
        await fetch(`${API}/api/interactive/clear`, { method: 'DELETE' });
        setState(null);
    };

    const handleGetState = async () => {
        const res = await fetch(`${API}/api/interactive/state`);
        const data = await res.json();
        setState(data);
    };

    return (
        <div>
            <h3>Interactive</h3>
            <p>Loads available protocols and parameter combinations from parsed data. Actual chart rendering happens in the browser.</p>

            <button onClick={handleFill} disabled={loading}>{loading ? 'Loading...' : 'Fill / Refresh'}</button>
            <button onClick={handleGetState}>Get State</button>
            <button onClick={handleClear}>Clear</button>

            {state?.error && <p>Error: {state.error}</p>}
            {state?.detail && <p>Error: {state.detail}</p>}

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
