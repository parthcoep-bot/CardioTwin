// CardioTwin — Main Application Container (Olive Green & Red Theme)
import React, { useState } from 'react';
import Navbar from './components/Navbar';
import PatientSidebar from './components/PatientSidebar';
import PatientHeader from './components/PatientHeader';
import DigitalTwinHeart from './components/DigitalTwinHeart';
import PredictiveRiskGauge from './components/PredictiveRiskGauge';
import VitalsTelemetryCharts from './components/VitalsTelemetryCharts';
import WhatIfSimulator from './components/WhatIfSimulator';
import AlertsAndProtocol from './components/AlertsAndProtocol';
import { mockPatients } from './data/mockPatients';

export default function App() {
  const [patients, setPatients] = useState(mockPatients);
  const [selectedPatientId, setSelectedPatientId] = useState(mockPatients[0].id);
  const [syncStatus, setSyncStatus] = useState(true);

  const activePatient = patients.find((p) => p.id === selectedPatientId) || patients[0];

  const handleRefresh = () => {
    setSyncStatus(false);
    setTimeout(() => {
      setSyncStatus(true);
    }, 800);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#f8faf6' }}>
      {/* Top Navbar */}
      <Navbar
        activePatient={activePatient}
        syncStatus={syncStatus}
        onRefresh={handleRefresh}
      />

      {/* Main Content Area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Patient Selection Sidebar */}
        <PatientSidebar
          patients={patients}
          selectedId={selectedPatientId}
          onSelect={setSelectedPatientId}
        />

        {/* Dashboard Workspace */}
        <main style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px 24px',
          maxHeight: 'calc(100vh - 67px)'
        }}>
          {/* Patient Overview Header */}
          <PatientHeader patient={activePatient} />

          {/* Grid: Twin Heart & Predictive Risk */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '16px', marginBottom: '16px' }}>
            <DigitalTwinHeart patient={activePatient} />
            <PredictiveRiskGauge patient={activePatient} />
          </div>

          {/* Full Width Vitals Telemetry Chart */}
          <div style={{ marginBottom: '16px' }}>
            <VitalsTelemetryCharts
              vitalsHistory={activePatient.vitalsHistory}
              patientRisk={activePatient.prediction.riskLevel}
            />
          </div>

          {/* Grid: What-If Simulation & Clinical Protocol */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <WhatIfSimulator patient={activePatient} />
            <AlertsAndProtocol patient={activePatient} />
          </div>

          {/* Summit Footer */}
          <footer style={{
            textAlign: 'center',
            padding: '16px 0',
            borderTop: '1px solid #e2e8dc',
            fontSize: '0.72rem',
            color: '#718067'
          }}>
            CardioTwin Proof-of-Concept • Built for Happiest Health Reimagining and Reforming Healthcare in India Summit 2026, Bengaluru
          </footer>
        </main>
      </div>
    </div>
  );
}
