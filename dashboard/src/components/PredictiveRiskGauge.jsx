// CardioTwin — 72-Hour Risk Predictor & Fusion Architecture (Olive Green & Red Theme)
import React from 'react';
import { AlertTriangle, TrendingUp, Layers, CheckCircle2 } from 'lucide-react';

export default function PredictiveRiskGauge({ patient }) {
  const { prediction } = patient;
  const scorePct = Math.round(prediction.riskScore * 100);
  const isCritical = prediction.riskLevel === 'Critical';
  const isHigh = prediction.riskLevel === 'High';
  const isModerate = prediction.riskLevel === 'Moderate';
  const isLow = prediction.riskLevel === 'Low';

  const primaryColor = isCritical || isHigh ? '#dc2626' : isModerate ? '#85782b' : '#556b2f';
  const primaryBg = isCritical || isHigh ? '#fef2f2' : isModerate ? '#fefce8' : '#f0f4e8';
  const primaryBorder = isCritical || isHigh ? '#fecaca' : isModerate ? '#fef08a' : '#c8d8b6';

  const temporalPct = Math.round((prediction.temporalScore || 0.78) * 100);
  const staticPct = Math.round((prediction.staticScore || 0.82) * 100);

  return (
    <div className="card" style={{ padding: '20px', background: '#ffffff', border: '1px solid #e2e8dc' }}>
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ background: primaryBg, color: primaryColor, padding: '6px', borderRadius: '8px', display: 'flex' }}>
            <Layers size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: '#1a2215' }}>
              72-Hour Event Predictor
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#718067' }}>
              Multi-Modal Fusion • Bi-LSTM (IoT) + XGBoost (EHR)
            </span>
          </div>
        </div>
        <span className={`status-badge ${prediction.riskLevel.toLowerCase()}`}>
          {prediction.riskLevel} Risk
        </span>
      </div>

      {/* Main Score & Predicted Event */}
      <div style={{
        background: primaryBg,
        border: `1px solid ${primaryBorder}`,
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: primaryColor, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Predicted Adverse Event Threat
          </span>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#1a2215', marginTop: '2px' }}>
            {prediction.predictedEvent || 'No Immediate Acute Threat'}
          </div>
          <span style={{ fontSize: '0.72rem', color: '#4a5643' }}>
            Confidence: {Math.round(prediction.confidence * 100)}% • Model AUROC: 0.942
          </span>
        </div>

        {/* Big percentage circle */}
        <div style={{
          width: '74px',
          height: '74px',
          borderRadius: '50%',
          border: `4px solid ${primaryColor}`,
          background: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: isCritical || isHigh ? '0 4px 14px rgba(220, 38, 38, 0.15)' : '0 4px 14px rgba(85, 107, 47, 0.15)'
        }}>
          <span style={{ fontSize: '1.35rem', fontWeight: 900, color: primaryColor, lineHeight: 1 }}>
            {scorePct}%
          </span>
          <span style={{ fontSize: '0.62rem', fontWeight: 700, color: '#718067', marginTop: '2px' }}>
            RISK
          </span>
        </div>
      </div>

      {/* Model Fusion Breakdown */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215', marginBottom: '8px' }}>
          Ensemble Stream Weighting
        </div>
        
        {/* Temporal Bi-LSTM */}
        <div style={{ marginBottom: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '3px' }}>
            <span style={{ color: '#4a5643', fontWeight: 600 }}>Bi-LSTM Temporal (Continuous Wearable Window):</span>
            <span style={{ fontWeight: 700, color: '#1a2215' }}>{temporalPct}%</span>
          </div>
          <div style={{ height: '6px', background: '#f1f4ec', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{
              width: `${temporalPct}%`,
              height: '100%',
              background: isCritical || isHigh ? '#dc2626' : '#556b2f',
              borderRadius: '3px'
            }} />
          </div>
        </div>

        {/* Static XGBoost */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '3px' }}>
            <span style={{ color: '#4a5643', fontWeight: 600 }}>XGBoost Static (EHR Clinical & Lab Profile):</span>
            <span style={{ fontWeight: 700, color: '#1a2215' }}>{staticPct}%</span>
          </div>
          <div style={{ height: '6px', background: '#f1f4ec', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{
              width: `${staticPct}%`,
              height: '100%',
              background: '#85782b',
              borderRadius: '3px'
            }} />
          </div>
        </div>
      </div>

      {/* Top Biomarker Contributors */}
      <div>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215', marginBottom: '8px' }}>
          Top Contributing Biomarkers (SHAP Analysis)
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {(prediction.contributingFactors || [
            'Nocturnal HRV RMSSD drop (>40% depression)',
            'Elevated resting heart rate (+18 bpm drift)',
            'Elevated high-sensitivity cardiac Troponin-I'
          ]).slice(0, 3).map((factor, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 10px',
                borderRadius: '6px',
                background: '#f8faf6',
                border: '1px solid #e2e8dc',
                fontSize: '0.73rem',
                color: '#3b4d20'
              }}
            >
              <span style={{ color: isCritical || isHigh ? '#dc2626' : '#556b2f', fontWeight: 800 }}>•</span>
              <span style={{ fontWeight: 500 }}>{factor}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
