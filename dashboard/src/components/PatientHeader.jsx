// CardioTwin — Patient Clinical Profile Header (Olive Green & Red Theme)
import React from 'react';
import { User, MapPin, Heart, Droplets, Pill, FileSpreadsheet } from 'lucide-react';

export default function PatientHeader({ patient }) {
  const { demographics, clinical, vitals } = patient;
  const isHighRisk = patient.prediction.riskLevel === 'Critical' || patient.prediction.riskLevel === 'High';

  return (
    <div className="card" style={{ padding: '18px 20px', background: '#ffffff', border: '1px solid #e2e8dc', marginBottom: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '14px' }}>
        {/* Left: Patient Details */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: isHighRisk ? '#fef2f2' : '#f0f4e8',
            color: isHighRisk ? '#dc2626' : '#556b2f',
            border: isHighRisk ? '1px solid #fecaca' : '1px solid #c8d8b6',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.1rem',
            fontWeight: 800
          }}>
            {patient.name.split(' ').map(n => n[0]).join('')}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#1a2215', margin: 0 }}>
                {patient.name}
              </h2>
              <span className={`status-badge ${patient.prediction.riskLevel.toLowerCase()}`}>
                {patient.prediction.riskLevel} Risk
              </span>
            </div>
            <div style={{ display: 'flex', gap: '14px', fontSize: '0.75rem', color: '#718067', marginTop: '3px', flexWrap: 'wrap' }}>
              <span>ID: <strong style={{ color: '#1a2215' }}>{patient.id}</strong></span>
              <span>Age: <strong style={{ color: '#1a2215' }}>{demographics.age}y</strong> ({demographics.gender})</span>
              <span>Location: <strong style={{ color: '#1a2215' }}>{demographics.city}, India</strong></span>
              <span>BMI: <strong style={{ color: '#1a2215' }}>{clinical.bmi} kg/m²</strong></span>
            </div>
          </div>
        </div>

        {/* Right: Key Clinical Baseline Badges */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <div style={{ background: '#f8faf6', border: '1px solid #e2e8dc', padding: '6px 12px', borderRadius: '8px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: '#718067', fontWeight: 700, display: 'block' }}>BLOOD PRESSURE</span>
            <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#1a2215' }}>{clinical.bloodPressure}</span>
          </div>

          <div style={{ background: '#f8faf6', border: '1px solid #e2e8dc', padding: '6px 12px', borderRadius: '8px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: '#718067', fontWeight: 700, display: 'block' }}>HbA1c</span>
            <span style={{ fontSize: '0.88rem', fontWeight: 800, color: Number(clinical.hba1c) > 7 ? '#dc2626' : '#556b2f' }}>
              {clinical.hba1c}%
            </span>
          </div>

          <div style={{ background: '#f8faf6', border: '1px solid #e2e8dc', padding: '6px 12px', borderRadius: '8px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: '#718067', fontWeight: 700, display: 'block' }}>TOTAL CHOLESTEROL</span>
            <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#1a2215' }}>{clinical.totalCholesterol} mg/dL</span>
          </div>

          <div style={{ background: '#f8faf6', border: '1px solid #e2e8dc', padding: '6px 12px', borderRadius: '8px', textAlign: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: '#718067', fontWeight: 700, display: 'block' }}>MEDICATIONS</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#556b2f' }}>
              {(clinical.medications || []).length} Prescribed
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
