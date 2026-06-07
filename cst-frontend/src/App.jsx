
import { useState } from 'react';
import ProtocolsTab from './components/ProtocolsTab';

export default function App() {

const [activeTab, setActiveTab] = useState('protocols');

  return (
    <div>
      <h1>Calibration Statistics Tool</h1>

      <nav>
        <button onClick={() => setActiveTab('protocols')}>
          Protocols
        </button>
        <button onClick={() => setActiveTab('limits')}>
          Limits
        </button>
        <button onClick={() => setActiveTab('stats')} style={{ color: 'blue' }}>
          Statistics
        </button>
      </nav>


      <div>
        {activeTab === 'protocols' && <ProtocolsTab />}
        {activeTab === 'limits' && <p>Limits Tab</p>}
        {activeTab === 'stats' && <p>Statistics Tab</p>}
      </div>
    </div>

  );
}