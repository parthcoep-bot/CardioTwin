// CardioTwin — Multi-Signal Wearable Charts (Olive Green & Red Theme)
import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine, AreaChart, Area
} from 'recharts';
import { Activity, Clock, ShieldAlert } from 'lucide-react';

export default function VitalsTelemetryCharts({ vitalsHistory, patientRisk }) {
  const [range, setRange] = useState('48h'); // '24h', '48h', '7d'
  const [activeMetric, setActiveMetric] = useState('heartRate'); // 'heartRate', 'hrv', 'spo2'

  // Filter history based on range
  const dataSlice = React.useMemo(() => {
    if (!vitalsHistory || vitalsHistory.length === 0) return [];
    if (range === '24h') return vitalsHistory.slice(-24);
    if (range === '48h') return vitalsHistory.slice(-48);
    return vitalsHistory;
  }, [vitalsHistory, range]);

  const formatTick = (ts, index) => {
    if (!ts) return '';
    const date = new Date(ts);
    return `${date.getHours().toString().padStart(2, '0')}:00`;
  };

  const isHighRisk = patientRisk === 'Critical' || patientRisk === 'High';

  return (
    <div className="card" style={{ padding: '20px', background: '#ffffff', border: '1px solid #e2e8dc' }}>
      {/* Header & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ background: '#f0f4e8', color: '#556b2f', padding: '6px', borderRadius: '8px', display: 'flex' }}>
            <Activity size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: '#1a2215' }}>
              Continuous Wearable IoT Telemetry
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#718067' }}>
              Hourly streaming physiological parameters • Anomaly detection active
            </span>
          </div>
        </div>

        {/* Metric Switcher & Time Range Tabs */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Metric Selector */}
          <div style={{ display: 'flex', background: '#f8faf6', borderRadius: '8px', padding: '2px', border: '1px solid #cbd5c0' }}>
            {[
              { id: 'heartRate', label: 'Heart Rate (BPM)' },
              { id: 'hrv', label: 'HRV RMSSD (ms)' },
              { id: 'spo2', label: 'SpO2 (%)' }
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => setActiveMetric(m.id)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '6px',
                  border: 'none',
                  background: activeMetric === m.id ? '#556b2f' : 'transparent',
                  color: activeMetric === m.id ? '#ffffff' : '#4a5643',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {m.label}
              </button>
            ))}
          </div>

          {/* Time Range Selector */}
          <div style={{ display: 'flex', background: '#f8faf6', borderRadius: '8px', padding: '2px', border: '1px solid #cbd5c0' }}>
            {['24h', '48h', '7d'].map((r) => (
              <button
                key={r}
                onClick={() => setRange(r)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '6px',
                  border: 'none',
                  background: range === r ? '#dc2626' : 'transparent',
                  color: range === r ? '#ffffff' : '#4a5643',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {r.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div style={{ width: '100%', height: '260px' }}>
        <ResponsiveContainer width="100%" height="100%">
          {activeMetric === 'heartRate' ? (
            <AreaChart data={dataSlice} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="hrGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={isHighRisk ? '#dc2626' : '#556b2f'} stopOpacity={0.25} />
                  <stop offset="95%" stopColor={isHighRisk ? '#dc2626' : '#556b2f'} stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f4ec" vertical={false} />
              <XAxis dataKey="timestamp" tickFormatter={formatTick} stroke="#8d9a84" fontSize={11} />
              <YAxis domain={['dataMin - 10', 'dataMax + 10']} stroke="#8d9a84" fontSize={11} />
              <Tooltip
                contentStyle={{ background: '#ffffff', border: '1px solid #cbd5c0', borderRadius: '8px', fontSize: '0.75rem' }}
                labelFormatter={(v) => new Date(v).toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                formatter={(val) => [`${val} bpm`, 'Heart Rate']}
              />
              <ReferenceLine y={100} stroke="#dc2626" strokeDasharray="4 4" label={{ value: 'Tachycardia (100)', fill: '#dc2626', fontSize: 10 }} />
              <ReferenceLine y={60} stroke="#556b2f" strokeDasharray="4 4" label={{ value: 'Bradycardia (60)', fill: '#556b2f', fontSize: 10 }} />
              <Area
                type="monotone"
                dataKey="heartRate"
                stroke={isHighRisk ? '#dc2626' : '#556b2f'}
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#hrGradient)"
              />
            </AreaChart>
          ) : activeMetric === 'hrv' ? (
            <LineChart data={dataSlice} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f4ec" vertical={false} />
              <XAxis dataKey="timestamp" tickFormatter={formatTick} stroke="#8d9a84" fontSize={11} />
              <YAxis domain={[0, 'dataMax + 15']} stroke="#8d9a84" fontSize={11} />
              <Tooltip
                contentStyle={{ background: '#ffffff', border: '1px solid #cbd5c0', borderRadius: '8px', fontSize: '0.75rem' }}
                labelFormatter={(v) => new Date(v).toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                formatter={(val) => [`${val} ms`, 'HRV RMSSD']}
              />
              <ReferenceLine y={25} stroke="#dc2626" strokeDasharray="4 4" label={{ value: 'Depressed Autonomic Tone (<25ms)', fill: '#dc2626', fontSize: 10 }} />
              <Line
                type="monotone"
                dataKey="hrv"
                stroke="#556b2f"
                strokeWidth={2.5}
                dot={false}
              />
            </LineChart>
          ) : (
            <LineChart data={dataSlice} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f4ec" vertical={false} />
              <XAxis dataKey="timestamp" tickFormatter={formatTick} stroke="#8d9a84" fontSize={11} />
              <YAxis domain={[85, 100]} stroke="#8d9a84" fontSize={11} />
              <Tooltip
                contentStyle={{ background: '#ffffff', border: '1px solid #cbd5c0', borderRadius: '8px', fontSize: '0.75rem' }}
                labelFormatter={(v) => new Date(v).toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                formatter={(val) => [`${val}%`, 'SpO2 Oxygen']}
              />
              <ReferenceLine y={94} stroke="#dc2626" strokeDasharray="4 4" label={{ value: 'Hypoxemia Alert (<94%)', fill: '#dc2626', fontSize: 10 }} />
              <Line
                type="monotone"
                dataKey="spo2"
                stroke="#3b4d20"
                strokeWidth={2.5}
                dot={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Mini Telemetry Status Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginTop: '12px',
        paddingTop: '10px',
        borderTop: '1px solid #f1f4ec',
        fontSize: '0.72rem',
        color: '#718067'
      }}>
        <span>Sampling interval: 1 Hour • Sensor streams: PPG, ECG Lead-I, 3D Accelerometer</span>
        <span style={{ color: isHighRisk ? '#dc2626' : '#556b2f', fontWeight: 600 }}>
          {isHighRisk ? '⚠ Significant circadian autonomic blunting detected' : '✓ Normal circadian nocturnal dipping'}
        </span>
      </div>
    </div>
  );
}
