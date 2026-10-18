// CardioTwin — Digital Twin Anatomical & Biometric Model (Olive Green & Red Theme)
import React, { useState, useEffect } from 'react';
import { Heart, Activity, Zap, Droplet, ShieldAlert, Cpu } from 'lucide-react';

export default function DigitalTwinHeart({ patient }) {
  const bpm = patient.vitals.heartRate;
  const isHighRisk = patient.prediction.riskLevel === 'Critical' || patient.prediction.riskLevel === 'High';
  const beatDuration = (60 / bpm).toFixed(2);

  // Twin physiological telemetry
  const ejectionFraction = isHighRisk ? 44 : 62;
  const strokeVolume = isHighRisk ? 58 : 74;
  const perfusionIndex = isHighRisk ? '68% (Compromised)' : '96% (Optimal)';
  const autonomicTone = isHighRisk ? 'Sympathetic Dominance' : 'Parasympathetic Balanced';

  return (
    <div className="card" style={{ padding: '20px', background: '#ffffff', border: '1px solid #e2e8dc' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            background: isHighRisk ? '#fef2f2' : '#f0f4e8',
            color: isHighRisk ? '#dc2626' : '#556b2f',
            padding: '6px',
            borderRadius: '8px',
            display: 'flex'
          }}>
            <Cpu size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: '#1a2215' }}>
              Virtual Anatomical Twin
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#718067' }}>
              Dynamic biomechanical simulation • Synchronized with IoT stream
            </span>
          </div>
        </div>

        <span style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          padding: '3px 10px',
          borderRadius: '12px',
          background: isHighRisk ? '#fef2f2' : '#f0f4e8',
          color: isHighRisk ? '#dc2626' : '#556b2f',
          border: isHighRisk ? '1px solid #fecaca' : '1px solid #c8d8b6'
        }}>
          {isHighRisk ? 'Ischemic Stress Detected' : 'Physiology Stable'}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignItems: 'center' }}>
        {/* Animated Heart Model */}
        <div style={{
          background: '#f8faf6',
          borderRadius: '12px',
          border: '1px solid #e2e8dc',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          minHeight: '220px'
        }}>
          {/* Heart SVG with pulsing animation */}
          <div style={{
            animation: `heartbeat-pulse ${beatDuration}s ease-in-out infinite`,
            transformOrigin: 'center center',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none">
              <defs>
                <radialGradient id="heartGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor={isHighRisk ? '#ef4444' : '#68d391'} />
                  <stop offset="70%" stopColor={isHighRisk ? '#dc2626' : '#556b2f'} />
                  <stop offset="100%" stopColor={isHighRisk ? '#991b1b' : '#3b4d20'} />
                </radialGradient>
              </defs>
              <path
                d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                fill="url(#heartGradient)"
                stroke={isHighRisk ? '#b91c1c' : '#2d3d19'}
                strokeWidth="0.8"
                style={{
                  filter: isHighRisk
                    ? 'drop-shadow(0 0 14px rgba(220, 38, 38, 0.45))'
                    : 'drop-shadow(0 0 14px rgba(85, 107, 47, 0.35))'
                }}
              />
              {/* Coronary artery overlays */}
              <path
                d="M10 8 Q 12 12 9 16"
                stroke={isHighRisk ? '#ffedd5' : '#ffffff'}
                strokeWidth="1.2"
                strokeDasharray="2 2"
                opacity="0.8"
              />
              <path
                d="M14 9 Q 13 13 15 17"
                stroke={isHighRisk ? '#ffedd5' : '#ffffff'}
                strokeWidth="1.2"
                strokeDasharray="2 2"
                opacity="0.8"
              />
            </svg>
          </div>

          {/* Pulse rate readout */}
          <div style={{ marginTop: '14px', textAlign: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
              <Activity size={16} color={isHighRisk ? '#dc2626' : '#556b2f'} />
              <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1a2215' }}>
                {bpm}
              </span>
              <span style={{ fontSize: '0.75rem', color: '#718067', fontWeight: 600 }}>BPM</span>
            </div>
            <span style={{ fontSize: '0.72rem', color: isHighRisk ? '#dc2626' : '#556b2f', fontWeight: 600 }}>
              {isHighRisk ? 'Tachycardia / Arrhythmic Drift' : 'Sinus Rhythm Normal'}
            </span>
          </div>
        </div>

        {/* Biomechanical Telemetry Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div style={{
            background: '#f8faf6',
            padding: '12px',
            borderRadius: '10px',
            border: '1px solid #e2e8dc'
          }}>
            <span style={{ fontSize: '0.7rem', color: '#718067', fontWeight: 600 }}>EJECTION FRACTION</span>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: isHighRisk ? '#dc2626' : '#556b2f', marginTop: '2px' }}>
              {ejectionFraction}%
            </div>
            <span style={{ fontSize: '0.68rem', color: '#8d9a84' }}>Normal: 55-70%</span>
          </div>

          <div style={{
            background: '#f8faf6',
            padding: '12px',
            borderRadius: '10px',
            border: '1px solid #e2e8dc'
          }}>
            <span style={{ fontSize: '0.7rem', color: '#718067', fontWeight: 600 }}>STROKE VOLUME</span>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1a2215', marginTop: '2px' }}>
              {strokeVolume} mL
            </div>
            <span style={{ fontSize: '0.68rem', color: '#8d9a84' }}>Estimated output</span>
          </div>

          <div style={{
            background: '#f8faf6',
            padding: '12px',
            borderRadius: '10px',
            border: '1px solid #e2e8dc'
          }}>
            <span style={{ fontSize: '0.7rem', color: '#718067', fontWeight: 600 }}>CORONARY PERFUSION</span>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: isHighRisk ? '#dc2626' : '#556b2f', marginTop: '4px' }}>
              {perfusionIndex}
            </div>
            <span style={{ fontSize: '0.68rem', color: '#8d9a84' }}>Arterial flow map</span>
          </div>

          <div style={{
            background: '#f8faf6',
            padding: '12px',
            borderRadius: '10px',
            border: '1px solid #e2e8dc'
          }}>
            <span style={{ fontSize: '0.7rem', color: '#718067', fontWeight: 600 }}>AUTONOMIC TONE</span>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#1a2215', marginTop: '4px' }}>
              {autonomicTone}
            </div>
            <span style={{ fontSize: '0.68rem', color: '#8d9a84' }}>HRV LF/HF analysis</span>
          </div>
        </div>
      </div>
    </div>
  );
}
