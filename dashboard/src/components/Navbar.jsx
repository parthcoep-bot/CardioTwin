// CardioTwin — Navigation & Summit Header (Olive Green & Red Theme)
import React from 'react';
import { Activity, ShieldCheck, HeartPulse, RefreshCw, Sparkles } from 'lucide-react';

export default function Navbar({ activePatient, syncStatus, onRefresh }) {
  return (
    <header style={{
      background: '#ffffff',
      borderBottom: '1px solid #e2e8dc',
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: '0 2px 8px rgba(40, 55, 25, 0.04)'
    }}>
      {/* Brand & Identity */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #556b2f 0%, #3b4d20 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          boxShadow: '0 4px 12px rgba(85, 107, 47, 0.25)'
        }}>
          <HeartPulse size={24} color="#ffffff" className="heart-beating" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1a2215', letterSpacing: '-0.02em' }}>
              Cardio<span style={{ color: '#dc2626' }}>Twin</span>
            </span>
            <span style={{
              background: '#f0f4e8',
              color: '#556b2f',
              border: '1px solid #c8d8b6',
              padding: '1px 8px',
              borderRadius: '9999px',
              fontSize: '0.68rem',
              fontWeight: 700,
              textTransform: 'uppercase'
            }}>
              PoC v1.0
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: '#718067', margin: 0, fontWeight: 500 }}>
            Cardiovascular Digital Twin & Proactive Risk Engine
          </p>
        </div>
      </div>

      {/* Summit Badge & Live Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          background: '#f0f4e8',
          border: '1px solid #c8d8b6',
          borderRadius: '8px',
          padding: '6px 14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Sparkles size={16} color="#556b2f" />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#3b4d20' }}>
            Happiest Health Summit 2026 • Bengaluru
          </span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          borderRadius: '8px',
          background: syncStatus ? '#f0f4e8' : '#fef2f2',
          border: syncStatus ? '1px solid #c8d8b6' : '1px solid #fecaca'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: syncStatus ? '#556b2f' : '#dc2626',
            display: 'inline-block',
            boxShadow: syncStatus ? '0 0 8px #556b2f' : '0 0 8px #dc2626'
          }} />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: syncStatus ? '#3b4d20' : '#991b1b' }}>
            {syncStatus ? 'Twin Synchronized' : 'Telemetry Alert'}
          </span>
        </div>

        <button
          onClick={onRefresh}
          className="btn-secondary"
          title="Refresh twin sensor streams"
          style={{ fontSize: '0.78rem', padding: '6px 12px' }}
        >
          <RefreshCw size={14} color="#556b2f" />
          <span>Sync IoT</span>
        </button>
      </div>
    </header>
  );
}
