// CardioTwin — Clinical Alerts & Proactive Protocol (Olive Green & Red Theme)
import React, { useState } from 'react';
import { AlertCircle, CheckCircle, ShieldAlert, FileText, Send, PhoneCall } from 'lucide-react';

export default function AlertsAndProtocol({ patient }) {
  const [transmitted, setTransmitted] = useState(false);
  const alerts = patient.alerts || [];
  const isHighRisk = patient.prediction.riskLevel === 'Critical' || patient.prediction.riskLevel === 'High';

  const handleTransmit = () => {
    setTransmitted(true);
    setTimeout(() => setTransmitted(false), 4000);
  };

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
            <ShieldAlert size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: '#1a2215' }}>
              Clinical Alerts & Proactive Protocol
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#718067' }}>
              Actionable guidance for treating physician • Cardiological society aligned
            </span>
          </div>
        </div>

        <button
          onClick={handleTransmit}
          className={isHighRisk ? 'btn-primary-red' : 'btn-primary-olive'}
          style={{ fontSize: '0.74rem', padding: '6px 12px' }}
        >
          {transmitted ? <CheckCircle size={14} /> : <Send size={14} />}
          <span>{transmitted ? 'Alert Dispatched' : 'Dispatch Clinician Alert'}</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Active Alerts List */}
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215', marginBottom: '8px' }}>
            Active Real-Time Anomaly Triggers ({alerts.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '190px', overflowY: 'auto' }}>
            {alerts.length === 0 ? (
              <div style={{ padding: '16px', textAlign: 'center', color: '#718067', fontSize: '0.75rem', background: '#f8faf6', borderRadius: '8px' }}>
                No active physiological alerts. Twin telemetry within normal bounds.
              </div>
            ) : (
              alerts.map((alert, idx) => {
                const isCrit = alert.severity === 'critical' || alert.severity === 'high';
                return (
                  <div
                    key={idx}
                    style={{
                      padding: '10px 12px',
                      borderRadius: '8px',
                      background: isCrit ? '#fef2f2' : '#f0f4e8',
                      border: isCrit ? '1px solid #fecaca' : '1px solid #c8d8b6',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px'
                    }}
                  >
                    <AlertCircle size={16} color={isCrit ? '#dc2626' : '#556b2f'} style={{ marginTop: '2px', flexShrink: 0 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: isCrit ? '#991b1b' : '#3b4d20' }}>
                          {alert.title || alert.type}
                        </span>
                        <span style={{ fontSize: '0.65rem', color: '#718067' }}>
                          {alert.timeAgo || 'Just now'}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.7rem', color: '#4a5643', margin: '2px 0 0 0' }}>
                        {alert.message || alert.description}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Recommended Proactive Actions */}
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1a2215', marginBottom: '8px' }}>
            Recommended Proactive Care Plan
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {[
              {
                step: '1',
                action: isHighRisk ? 'Immediate 12-lead ECG & emergency cardiology consult' : 'Routine 6-month preventive cardiology follow-up',
                priority: isHighRisk ? 'Urgent' : 'Routine'
              },
              {
                step: '2',
                action: isHighRisk ? 'Review antiplatelet therapy & initiate high-intensity statin' : 'Continue current lifestyle & walking regimen (5k steps)',
                priority: isHighRisk ? 'Urgent' : 'Optimal'
              },
              {
                step: '3',
                action: isHighRisk ? 'Schedule continuous 48-hr ambulatory Holter monitoring' : 'Bi-weekly BP & glucose logging via wearable app',
                priority: isHighRisk ? 'Moderate' : 'Routine'
              }
            ].map((item) => (
              <div
                key={item.step}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '8px 10px',
                  borderRadius: '8px',
                  background: '#f8faf6',
                  border: '1px solid #e2e8dc',
                  fontSize: '0.72rem'
                }}
              >
                <span style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background: isHighRisk && item.priority === 'Urgent' ? '#dc2626' : '#556b2f',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '0.68rem',
                  flexShrink: 0
                }}>
                  {item.step}
                </span>
                <span style={{ flex: 1, color: '#1a2215', fontWeight: 500 }}>
                  {item.action}
                </span>
                <span style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  color: isHighRisk && item.priority === 'Urgent' ? '#dc2626' : '#556b2f',
                  textTransform: 'uppercase'
                }}>
                  {item.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
