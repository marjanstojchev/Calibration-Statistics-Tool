
import { useState } from 'react';
import ThemeToggle from './components/ThemeToggle';
import ProtocolsTab from './components/ProtocolsTab';
import LimitsTab from './components/LimitsTab';
import SystemDiagramsTab from './components/SystemDiagramsTab';
import TxDiagramsTab from './components/TxDiagramsTab';
import HuellkurvenTab from './components/HuellkurvenTab';
import AntennaPatternTab from './components/AntennaPatternTab';
import InteractiveTab from './components/InteractiveTab';
import StatisticsTab from './components/StatisticsTab';
import LogsPanel from './components/LogsPanel';

// ── Tab icons (inline SVG) ──────────────────────────────────
const Icon = ({ d, d2 }) => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d={d}/>{d2 && <path d={d2}/>}
    </svg>
);

const TABS = [
    { key: 'protocols',        label: 'Protocols',        icon: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z', icon2: 'M14 2v6h6' },
    { key: 'limits',           label: 'Limits',           icon: 'M3 3v18h18', icon2: 'M18.7 8l-5.1 5.2-2.8-2.7L7 14.3' },
    { key: 'system_diagrams',  label: 'System Diagrams',  icon: 'M1 6l11 12 11-12' },
    { key: 'tx_diagrams',      label: 'TX Diagrams',      icon: 'M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.15 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.07 2.18h3a2 2 0 0 1 2 1.72' },
    { key: 'huellkurven',      label: 'Hüllkurven',      icon: 'M2 20h.01M7 20v-4M12 20v-8M17 20V8M22 4v16' },
    { key: 'antenna_patterns', label: 'Ant. Patterns',    icon: 'M12 2a10 10 0 1 0 10 10', icon2: 'M12 12l6-6' },
    { key: 'interactive',      label: 'Interactive',      icon: 'M18 20V10M12 20V4M6 20v-6' },
    { key: 'statistics',       label: 'Statistics',       icon: 'M12 20V10M18 20V4M6 20v-4' },
    { key: 'logs',             label: 'Logs',             icon: 'M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z' },
];

export default function App() {
    const [activeTab, setActiveTab] = useState('protocols');

    return (
        <div className="app-shell">
            {/* ── Header ───────────────────────────────────── */}
            <header className="app-header">
                <div className="app-header-left">
                    <div className="app-logo">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                        </svg>
                    </div>
                    <span className="app-title">Calibration Statistics Tool</span>
                    <span className="app-subtitle">RF Measurement Analysis</span>
                </div>
                <ThemeToggle />
            </header>

            {/* ── Tab Navigation ───────────────────────────── */}
            <nav className="app-nav">
                {TABS.map(tab => (
                    <button key={tab.key}
                        className={`nav-btn ${activeTab === tab.key ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.key)}>
                        <Icon d={tab.icon} d2={tab.icon2} />
                        {tab.label}
                    </button>
                ))}
            </nav>

            {/* ── Content ──────────────────────────────────── */}
            <main className="app-content">
                {activeTab === 'protocols'        && <ProtocolsTab />}
                {activeTab === 'limits'           && <LimitsTab />}
                {activeTab === 'system_diagrams'  && <SystemDiagramsTab />}
                {activeTab === 'tx_diagrams'      && <TxDiagramsTab />}
                {activeTab === 'huellkurven'      && <HuellkurvenTab />}
                {activeTab === 'antenna_patterns' && <AntennaPatternTab />}
                {activeTab === 'interactive'      && <InteractiveTab />}
                {activeTab === 'statistics'       && <StatisticsTab />}
                {activeTab === 'logs'             && <LogsPanel />}
            </main>
        </div>
    );
}