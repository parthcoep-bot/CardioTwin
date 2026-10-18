// CardioTwin — Patient Roster Sidebar (Olive Green & Red Theme)
import React, { useState } from 'react';
import { Search, User, AlertCircle, Heart } from 'lucide-react';

export default function PatientSidebar({ patients, selectedId, onSelect }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('All');

  const filtered = patients.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
                          p.id.toLowerCase().includes(search.toLowerCase()) ||
                          p.demographics.city.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'All' || p.prediction.riskLevel === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <aside style={{
      width: '320px',
      background: '#ffffff',
      borderRight: '1px solid #e2e8dc',
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 67px)',
      boxShadow: '2px 0 8px rgba(40, 55, 25, 0.02)'
    }}>
      {/* Sidebar Header & Search */}
      <div style={{ padding: '16px', borderBottom: '1px solid #e2e8dc' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1a2215', margin: 0 }}>
            Patient Twins ({filtered.length})
          </h2>
          <span style={{ fontSize: '0.72rem', color: '#556b2f', fontWeight: 600, background: '#f0f4e8', padding: '2px 8px', borderRadius: '12px' }}>
            Live EHR Feed
          </span>
        </div>

        {/* Search input */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: '#f8faf6',
          border: '1px solid #cbd5c0',
          borderRadius: '8px',
          padding: '6px 10px',
          marginBottom: '10px'
        }}>
          <Search size={15} color="#718067" />
          <input
            type="text"
            placeholder="Search patient or city..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              border: 'none',
              background: 'transparent',
              outline: 'none',
              width: '100%',
              fontSize: '0.8rem',
              color: '#1a2215'
            }}
          />
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
          {['All', 'Critical', 'High', 'Moderate', 'Low'].map((cat) => {
            const isActive = filter === cat;
            let activeBg = '#556b2f';
            if (cat === 'Critical') activeBg = '#dc2626';
            if (cat === 'High') activeBg = '#c2410c';

            return (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                style={{
                  padding: '3px 10px',
                  borderRadius: '12px',
                  border: isActive ? `1px solid ${activeBg}` : '1px solid #cbd5c0',
                  background: isActive ? activeBg : '#ffffff',
                  color: isActive ? '#ffffff' : '#4a5643',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s'
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* Patient List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
        {filtered.map((patient) => {
          const isSelected = patient.id === selectedId;
          const isCritical = patient.prediction.riskLevel === 'Critical';
          const isHigh = patient.prediction.riskLevel === 'High';
          const isLow = patient.prediction.riskLevel === 'Low';

          return (
            <div
              key={patient.id}
              onClick={() => onSelect(patient.id)}
              style={{
                padding: '12px',
                borderRadius: '10px',
                marginBottom: '8px',
                cursor: 'pointer',
                background: isSelected ? '#f0f4e8' : '#ffffff',
                border: isSelected
                  ? '2px solid #556b2f'
                  : '1px solid #e2e8dc',
                borderLeft: isCritical
                  ? '4px solid #dc2626'
                  : isHigh
                  ? '4px solid #c2410c'
                  : '4px solid #556b2f',
                boxShadow: isSelected ? '0 4px 12px rgba(85, 107, 47, 0.12)' : '0 1px 3px rgba(0,0,0,0.02)',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                <div>
                  <h3 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#1a2215', margin: 0 }}>
                    {patient.name}
                  </h3>
                  <span style={{ fontSize: '0.72rem', color: '#718067' }}>
                    {patient.demographics.age}y, {patient.demographics.gender} • {patient.demographics.city}
                  </span>
                </div>
                <span className={`status-badge ${patient.prediction.riskLevel.toLowerCase()}`}>
                  {patient.prediction.riskLevel}
                </span>
              </div>

              <div style={{ fontSize: '0.74rem', color: '#4a5643', marginTop: '6px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                <span style={{ fontWeight: 600 }}>Diagnosis:</span> {patient.clinical.primaryDiagnosis}
              </div>

              {/* Mini Vitals Row */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '8px',
                paddingTop: '6px',
                borderTop: '1px dashed #e2e8dc',
                fontSize: '0.7rem'
              }}>
                <span style={{ color: isCritical ? '#dc2626' : '#556b2f', fontWeight: 600 }}>
                  HR: {patient.vitals.heartRate} bpm
                </span>
                <span style={{ color: '#4a5643' }}>
                  BP: {patient.clinical.bloodPressure}
                </span>
                <span style={{ color: '#556b2f', fontWeight: 600 }}>
                  SpO2: {patient.vitals.spo2}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
