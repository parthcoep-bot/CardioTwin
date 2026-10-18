// CardioTwin — What-If Intervention Simulator (Olive Green & Red Theme)
import React, { useState } from 'react';
import { Sliders, Play, RotateCcw, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

export default function WhatIfSimulator({ patient }) {
  const baseScore = Math.round(patient.prediction.riskScore * 100);

  // Intervention adjustments
  const [statinDose, setStatinDose] = useState(false);
  const [bpReduction, setBpReduction] = useState(0); // 0, 10, 20 mmHg
  const [sleepImprovement, setSleepImprovement] = useState(0); // 0, 1, 2 hours
  const [dailySteps, setDailySteps] = useState(0); // 0, 3000, 6000 steps

  // Calculate simulated risk reduction
  let reduction = 0;
  if (statinDose) reduction += 18;
  reduction += bpReduction * 1.1;
  reduction += sleepImprovement * 5;
  reduction += (dailySteps / 1000) * 2.5;

  const simulatedScore = Math.max(8, Math.min(baseScore, Math.round(baseScore - reduction)));
  const delta = baseScore - simulatedScore;

  const handleReset = () => {
    setStatinDose(false);
    setBpReduction(0);
    setSleepImprovement(0);
    setDailySteps(0);
  };

  const isSimulatedLow = simulatedScore < 30;
  const isSimulatedModerate = simulatedScore >= 30 && simulatedScore < 60;

  return (
    <div className="card" style={{ padding: '20px', background: '#ffffff', border: '1px solid #e2e8dc' }}>
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ background: '#f0f4e8', color: '#556b2f', padding: '6px', borderRadius: '8px', display: 'flex' }}>
            <Sliders size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: '#1a2215' }}>
              What-If Digital Twin Simulator
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#718067' }}>
              Simulate clinical interventions & counterfactual outcomes in real-time
            </span>
          </div>
        </div>

        <button
          onClick={handleReset}
          className="btn-secondary"
          style={{ fontSize: '0.72rem', padding: '4px 10px' }}
        >
          <RotateCcw size={13} />
          Reset
        </button>
      </div>

      {/* Before vs After Score Comparison Banner */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr auto 1fr',
        gap: '12px',
        alignItems: 'center',
        background: '#f8faf6',
        border: '1px solid #e2e8dc',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px'
      }}>
        {/* Baseline State */}
        <div style={{ textAlign: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#718067', fontWeight: 700, textTransform: 'uppercase' }}>
            Current Baseline Twin
          </span>
          <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#dc2626', marginTop: '2px' }}>
            {baseScore}%
          </div>
          <span style={{ fontSize: '0.7rem', color: '#dc2626', fontWeight: 600 }}>
            {patient.prediction.riskLevel} Risk
          </span>
        </div>

        <ArrowRight size={22} color="#556b2f" />

        {/* Counterfactual Simulated State */}
        <div style={{ textAlign: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#718067', fontWeight: 700, textTransform: 'uppercase' }}>
            Projected Post-Intervention
          </span>
          <div style={{
            fontSize: '1.6rem',
            fontWeight: 900,
            color: isSimulatedLow ? '#556b2f' : isSimulatedModerate ? '#85782b' : '#dc2626',
            marginTop: '2px'
          }}>
            {simulatedScore}%
          </div>
          <span style={{
            fontSize: '0.7rem',
            color: '#556b2f',
            fontWeight: 700,
            background: '#f0f4e8',
            padding: '2px 8px',
            borderRadius: '10px'
          }}>
            -{delta}% Risk Abatement
          </span>
        </div>
      </div>

      {/* Simulator Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
        {/* Medication Titration */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8dc', padding: '12px', borderRadius: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215' }}>
              Statin Intensification
            </span>
            <input
              type="checkbox"
              checked={statinDose}
              onChange={(e) => setStatinDose(e.target.checked)}
              style={{ accentColor: '#556b2f', width: '16px', height: '16px', cursor: 'pointer' }}
            />
          </div>
          <p style={{ fontSize: '0.7rem', color: '#718067', margin: 0 }}>
            Titrate to Atorvastatin 80mg + Ezetimibe 10mg (-18% absolute risk)
          </p>
        </div>

        {/* BP Target Normalization */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8dc', padding: '12px', borderRadius: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215' }}>
              Systolic BP Reduction
            </span>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#556b2f' }}>
              -{bpReduction} mmHg
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="25"
            step="5"
            value={bpReduction}
            onChange={(e) => setBpReduction(Number(e.target.value))}
            style={{ width: '100%', accentColor: '#556b2f', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: '#8d9a84' }}>
            <span>0 mmHg</span>
            <span>Target: &lt;120/80</span>
            <span>-25 mmHg</span>
          </div>
        </div>

        {/* Sleep & Circadian Hygiene */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8dc', padding: '12px', borderRadius: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215' }}>
              Sleep & Rest Extension
            </span>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#556b2f' }}>
              +{sleepImprovement} hrs
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="3"
            step="1"
            value={sleepImprovement}
            onChange={(e) => setSleepImprovement(Number(e.target.value))}
            style={{ width: '100%', accentColor: '#556b2f', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: '#8d9a84' }}>
            <span>Current</span>
            <span>+3 Hours</span>
          </div>
        </div>

        {/* Physical Mobility / Steps */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8dc', padding: '12px', borderRadius: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215' }}>
              Daily Step Mobility
            </span>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#556b2f' }}>
              +{dailySteps} steps
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="6000"
            step="1500"
            value={dailySteps}
            onChange={(e) => setDailySteps(Number(e.target.value))}
            style={{ width: '100%', accentColor: '#556b2f', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: '#8d9a84' }}>
            <span>Sedentary</span>
            <span>Active (+6k)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
