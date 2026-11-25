import React from 'react';
import { Radio, RefreshCw, Sparkles, CheckCircle2 } from 'lucide-react';

export default function Header({ isHealthy, checkingHealth, onNewSession, activeSessionId }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo-group">
          <div className="logo-badge">
            <Radio size={22} />
          </div>
          <div className="logo-text">
            <h1>PodResearch 2.0</h1>
            <p>Autonomous YouTube Article Generator & Human-in-the-Loop Review</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="status-badge">
            <span className={`status-dot ${isHealthy ? 'online' : 'offline'}`} />
            <span>{isHealthy ? 'Backend Connected' : 'Backend Disconnected'}</span>
          </div>

          {activeSessionId && (
            <button className="btn btn-outline btn-sm" onClick={onNewSession}>
              <RefreshCw size={14} /> New Session
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
