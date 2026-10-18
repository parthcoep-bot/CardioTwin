/**
 * CardioTwin — Mock Patient Data
 * 
 * Realistic synthetic patient profiles for dashboard demonstration.
 * Includes 7-day vitals time-series, risk scores, alerts, and clinical context.
 */

// Generate 7 days of hourly vital signs
function generateVitals(baseHR, baseHRV, baseSPO2, riskLevel, eventType) {
  const vitals = [];
  const now = new Date();

  for (let d = 6; d >= 0; d--) {
    for (let h = 0; h < 24; h++) {
      const timestamp = new Date(now);
      timestamp.setDate(timestamp.getDate() - d);
      timestamp.setHours(h, 0, 0, 0);

      // Circadian pattern
      let hrMod = 0;
      let hrvMod = 1.0;
      if (h >= 0 && h < 6) { hrMod = -12; hrvMod = 1.3; }
      else if (h >= 6 && h < 9) { hrMod = -5 + (h - 6) * 5; hrvMod = 1.0; }
      else if (h >= 9 && h < 18) { hrMod = 5 + Math.sin((h - 9) * Math.PI / 9) * 8; hrvMod = 0.85; }
      else if (h >= 18 && h < 22) { hrMod = 3 - (h - 18) * 2; hrvMod = 1.0; }
      else { hrMod = -8; hrvMod = 1.1; }

      // Anomaly injection for last 48 hours of high-risk patients
      let anomalyFactor = 0;
      if ((riskLevel === 'Critical' || riskLevel === 'High') && d <= 1) {
        anomalyFactor = (2 - d) * 0.3 + (h / 24) * 0.2;
      }

      const hr = Math.max(45, Math.min(160,
        baseHR + hrMod + (Math.random() - 0.5) * 6 + anomalyFactor * 25
      ));
      const hrv = Math.max(8, 
        baseHRV * hrvMod + (Math.random() - 0.5) * 5 - anomalyFactor * 15
      );
      const spo2 = Math.max(88, Math.min(100,
        baseSPO2 + (Math.random() - 0.5) * 1 - anomalyFactor * 3
      ));
      const respRate = Math.max(10, Math.min(30,
        16 + (Math.random() - 0.5) * 3 + anomalyFactor * 5
      ));
      const steps = h >= 6 && h <= 22
        ? Math.max(0, Math.floor(Math.random() * 800 * (1 - anomalyFactor * 0.5)))
        : 0;
      const sleepStage = h >= 23 || h < 7
        ? Math.floor(Math.random() * 4)
        : 0;
      const skinTemp = +(Math.random() * 0.8 - 0.4 - anomalyFactor * 0.5).toFixed(2);
      const stress = Math.min(100, Math.max(0,
        20 + (100 - hrv) * 0.3 + (hr - 70) * 0.4 + anomalyFactor * 30
      ));

      vitals.push({
        timestamp: timestamp.toISOString(),
        hour: h,
        day: 6 - d,
        dayLabel: timestamp.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' }),
        heartRate: +hr.toFixed(1),
        hrvSDNN: +hrv.toFixed(1),
        spo2: +spo2.toFixed(1),
        respiratoryRate: +respRate.toFixed(1),
        stepCount: steps,
        sleepStage,
        skinTempDelta: skinTemp,
        stressScore: +stress.toFixed(1),
      });
    }
  }
  return vitals;
}

// Generate daily aggregates for timeline chart
function generateDailyAggregates(vitals) {
  const days = {};
  vitals.forEach(v => {
    const key = v.dayLabel;
    if (!days[key]) {
      days[key] = { hrs: [], hrvs: [], spo2s: [], steps: 0, stress: [], label: key };
    }
    days[key].hrs.push(v.heartRate);
    days[key].hrvs.push(v.hrvSDNN);
    days[key].spo2s.push(v.spo2);
    days[key].steps += v.stepCount;
    days[key].stress.push(v.stressScore);
  });

  return Object.values(days).map(d => ({
    day: d.label,
    avgHR: +(d.hrs.reduce((a, b) => a + b, 0) / d.hrs.length).toFixed(1),
    minHR: +Math.min(...d.hrs).toFixed(1),
    maxHR: +Math.max(...d.hrs).toFixed(1),
    avgHRV: +(d.hrvs.reduce((a, b) => a + b, 0) / d.hrvs.length).toFixed(1),
    avgSPO2: +(d.spo2s.reduce((a, b) => a + b, 0) / d.spo2s.length).toFixed(1),
    totalSteps: d.steps,
    avgStress: +(d.stress.reduce((a, b) => a + b, 0) / d.stress.length).toFixed(1),
  }));
}

export const mockPatients = [
  {
    id: 'P0001',
    name: 'Rajesh Kumar Sharma',
    age: 58,
    gender: 'Male',
    state: 'Karnataka',
    bloodGroup: 'B+',
    bmi: 29.4,
    photo: null,
    riskScore: 82,
    riskLevel: 'Critical',
    riskTrend: 'rising',
    eventType: 'Acute Coronary Syndrome',
    confidence: 0.91,
    temporalScore: 0.88,
    staticScore: 0.79,
    lastUpdated: '2 min ago',
    // EHR Data
    ehr: {
      systolicBP: 158,
      diastolicBP: 96,
      restingHR: 82,
      diagnoses: ['I10 — Essential hypertension', 'E11.9 — Type 2 Diabetes', 'E78.5 — Dyslipidemia', 'E66.01 — Obesity'],
      medications: [
        { name: 'Telmisartan 80mg', class: 'ARB', adherence: 78 },
        { name: 'Atorvastatin 40mg', class: 'Statin', adherence: 85 },
        { name: 'Metformin 1000mg', class: 'Antidiabetic', adherence: 72 },
        { name: 'Aspirin 75mg', class: 'Antiplatelet', adherence: 90 },
      ],
      labs: {
        totalCholesterol: 268,
        hdl: 34,
        ldl: 175,
        triglycerides: 245,
        fastingGlucose: 168,
        hba1c: 8.2,
        creatinine: 1.3,
        egfr: 62,
        crp: 4.8,
        bnp: 320,
        troponin: 0.02,
      },
      framinghamRisk: 38.5,
      familyHistoryCVD: true,
      smoker: true,
      physicalActivity: 'Sedentary',
    },
    alerts: [
      { id: 1, severity: 'critical', title: 'Acute Coronary Risk Elevated', message: 'Fused risk score has crossed critical threshold (82/100). HRV declining rapidly over 48 hours combined with elevated resting HR. Troponin trending upward.', time: '12 min ago', action: 'Pre-alert cardiac unit. Advise patient to seek emergency care if chest pain develops.' },
      { id: 2, severity: 'high', title: 'HRV Sustained Decline', message: 'Heart Rate Variability (SDNN) has dropped 40% below 7-day baseline. Sustained sympathetic dominance detected.', time: '3 hours ago', action: 'Review current medication. Consider adding beta-blocker.' },
      { id: 3, severity: 'moderate', title: 'Medication Adherence Alert', message: 'Metformin adherence dropped to 72%. Fasting glucose trending above 160 mg/dL.', time: '1 day ago', action: 'Schedule patient counseling. Consider medication review.' },
    ],
    riskFactors: [
      { name: 'HRV Decline (48h)', contribution: 28, color: '#6366f1' },
      { name: 'Elevated LDL', contribution: 18, color: '#f43f5e' },
      { name: 'Poor Glycemic Control', contribution: 15, color: '#f59e0b' },
      { name: 'Smoking Status', contribution: 14, color: '#ef4444' },
      { name: 'Hypertension', contribution: 12, color: '#ec4899' },
      { name: 'Family History CVD', contribution: 8, color: '#8b5cf6' },
      { name: 'Sedentary Lifestyle', contribution: 5, color: '#06b6d4' },
    ],
    recommendation: 'EMERGENCY: Pre-alert nearest cardiac care unit. Advise patient to seek immediate care if chest pain, shortness of breath, or arm numbness develops. Schedule urgent troponin retest and ECG within 6 hours.',
  },
  {
    id: 'P0042',
    name: 'Priya Venkatesh',
    age: 45,
    gender: 'Female',
    state: 'Tamil Nadu',
    bloodGroup: 'O+',
    bmi: 26.1,
    photo: null,
    riskScore: 61,
    riskLevel: 'High',
    riskTrend: 'rising',
    eventType: 'Arrhythmia',
    confidence: 0.85,
    temporalScore: 0.76,
    staticScore: 0.52,
    lastUpdated: '8 min ago',
    ehr: {
      systolicBP: 142,
      diastolicBP: 88,
      restingHR: 78,
      diagnoses: ['I10 — Essential hypertension', 'I48.91 — Atrial fibrillation', 'G47.33 — Obstructive sleep apnea'],
      medications: [
        { name: 'Amlodipine 5mg', class: 'CCB', adherence: 92 },
        { name: 'Warfarin 2mg', class: 'Anticoagulant', adherence: 88 },
        { name: 'Metoprolol 50mg', class: 'Beta-blocker', adherence: 85 },
      ],
      labs: {
        totalCholesterol: 215,
        hdl: 52,
        ldl: 132,
        triglycerides: 158,
        fastingGlucose: 98,
        hba1c: 5.6,
        creatinine: 0.9,
        egfr: 85,
        crp: 2.1,
        bnp: 180,
        troponin: 0.01,
      },
      framinghamRisk: 18.2,
      familyHistoryCVD: true,
      smoker: false,
      physicalActivity: 'Light',
    },
    alerts: [
      { id: 1, severity: 'high', title: 'Arrhythmia Pattern Detected', message: 'Irregular HRV patterns consistent with pre-AFib episodes detected. Heart rate showing intermittent spikes inconsistent with activity level.', time: '25 min ago', action: 'Schedule Holter monitoring within 48 hours.' },
      { id: 2, severity: 'moderate', title: 'Sleep Quality Deteriorating', message: 'Deep sleep percentage has declined 35% over past week. Likely exacerbating existing sleep apnea and AFib risk.', time: '6 hours ago', action: 'Evaluate CPAP compliance. Consider sleep study.' },
    ],
    riskFactors: [
      { name: 'Irregular HRV Pattern', contribution: 32, color: '#6366f1' },
      { name: 'Atrial Fibrillation Hx', contribution: 22, color: '#f43f5e' },
      { name: 'Sleep Apnea', contribution: 18, color: '#8b5cf6' },
      { name: 'Hypertension', contribution: 15, color: '#ec4899' },
      { name: 'Sleep Quality Decline', contribution: 8, color: '#06b6d4' },
      { name: 'Family History CVD', contribution: 5, color: '#f59e0b' },
    ],
    recommendation: 'Schedule ECG and Holter monitoring within 48 hours. Review Warfarin INR levels. Assess CPAP compliance for sleep apnea management. Consider increasing Metoprolol if AFib episodes persist.',
  },
  {
    id: 'P0107',
    name: 'Arjun Patel',
    age: 52,
    gender: 'Male',
    state: 'Gujarat',
    bloodGroup: 'A+',
    bmi: 31.8,
    photo: null,
    riskScore: 44,
    riskLevel: 'Moderate',
    riskTrend: 'stable',
    eventType: 'Hypertensive Crisis',
    confidence: 0.78,
    temporalScore: 0.38,
    staticScore: 0.51,
    lastUpdated: '22 min ago',
    ehr: {
      systolicBP: 148,
      diastolicBP: 92,
      restingHR: 76,
      diagnoses: ['I10 — Essential hypertension', 'E11.9 — Type 2 Diabetes', 'E78.0 — Hypercholesterolemia'],
      medications: [
        { name: 'Ramipril 5mg', class: 'ACE-inhibitor', adherence: 88 },
        { name: 'Rosuvastatin 10mg', class: 'Statin', adherence: 91 },
        { name: 'Metformin 850mg', class: 'Antidiabetic', adherence: 82 },
      ],
      labs: {
        totalCholesterol: 232,
        hdl: 41,
        ldl: 148,
        triglycerides: 198,
        fastingGlucose: 135,
        hba1c: 7.1,
        creatinine: 1.1,
        egfr: 74,
        crp: 2.8,
        bnp: 95,
        troponin: 0.005,
      },
      framinghamRisk: 24.1,
      familyHistoryCVD: false,
      smoker: false,
      physicalActivity: 'Light',
    },
    alerts: [
      { id: 1, severity: 'moderate', title: 'BP Trend Elevated', message: 'Resting heart rate trending 8% above baseline over the past week. Combined with existing hypertension, monitoring for hypertensive crisis.', time: '2 hours ago', action: 'Increase BP monitoring frequency. Review Ramipril dose.' },
    ],
    riskFactors: [
      { name: 'Hypertension', contribution: 25, color: '#ec4899' },
      { name: 'Elevated BMI', contribution: 20, color: '#f59e0b' },
      { name: 'Diabetes', contribution: 18, color: '#f43f5e' },
      { name: 'Elevated LDL', contribution: 15, color: '#6366f1' },
      { name: 'Low HDL', contribution: 12, color: '#06b6d4' },
      { name: 'Sedentary Tendency', contribution: 10, color: '#8b5cf6' },
    ],
    recommendation: 'Increase BP monitoring to twice daily. Review Ramipril dosage — consider uptitration to 10mg. Reinforce dietary counseling (DASH diet). Target weight reduction of 5kg over next 3 months.',
  },
  {
    id: 'P0235',
    name: 'Meera Krishnan',
    age: 38,
    gender: 'Female',
    state: 'Kerala',
    bloodGroup: 'AB+',
    bmi: 23.2,
    photo: null,
    riskScore: 14,
    riskLevel: 'Low',
    riskTrend: 'stable',
    eventType: 'None',
    confidence: 0.94,
    temporalScore: 0.08,
    staticScore: 0.12,
    lastUpdated: '45 min ago',
    ehr: {
      systolicBP: 118,
      diastolicBP: 76,
      restingHR: 68,
      diagnoses: [],
      medications: [],
      labs: {
        totalCholesterol: 192,
        hdl: 58,
        ldl: 110,
        triglycerides: 120,
        fastingGlucose: 88,
        hba1c: 5.2,
        creatinine: 0.8,
        egfr: 98,
        crp: 0.8,
        bnp: 35,
        troponin: 0.003,
      },
      framinghamRisk: 4.2,
      familyHistoryCVD: false,
      smoker: false,
      physicalActivity: 'Active',
    },
    alerts: [],
    riskFactors: [
      { name: 'Age Factor', contribution: 35, color: '#06b6d4' },
      { name: 'Mild LDL Elevation', contribution: 25, color: '#6366f1' },
      { name: 'Genetic Baseline', contribution: 20, color: '#8b5cf6' },
      { name: 'Stress Variability', contribution: 20, color: '#f59e0b' },
    ],
    recommendation: 'No intervention needed. Continue current lifestyle. Annual cardiovascular screening recommended. Next routine check in 6 months.',
  },
  {
    id: 'P0312',
    name: 'Suresh Reddy',
    age: 65,
    gender: 'Male',
    state: 'Telangana',
    bloodGroup: 'O+',
    bmi: 27.6,
    photo: null,
    riskScore: 71,
    riskLevel: 'High',
    riskTrend: 'rising',
    eventType: 'Hypertensive Crisis',
    confidence: 0.87,
    temporalScore: 0.68,
    staticScore: 0.74,
    lastUpdated: '5 min ago',
    ehr: {
      systolicBP: 165,
      diastolicBP: 100,
      restingHR: 84,
      diagnoses: ['I10 — Essential hypertension', 'I11.9 — Hypertensive heart disease', 'I25.10 — CAD', 'E78.5 — Dyslipidemia', 'N18.3 — CKD Stage 3'],
      medications: [
        { name: 'Telmisartan 80mg', class: 'ARB', adherence: 76 },
        { name: 'Amlodipine 10mg', class: 'CCB', adherence: 80 },
        { name: 'Atorvastatin 80mg', class: 'Statin', adherence: 88 },
        { name: 'Aspirin 150mg', class: 'Antiplatelet', adherence: 92 },
        { name: 'Metoprolol 100mg', class: 'Beta-blocker', adherence: 75 },
      ],
      labs: {
        totalCholesterol: 248,
        hdl: 36,
        ldl: 162,
        triglycerides: 220,
        fastingGlucose: 112,
        hba1c: 6.1,
        creatinine: 1.6,
        egfr: 48,
        crp: 5.2,
        bnp: 450,
        troponin: 0.015,
      },
      framinghamRisk: 42.8,
      familyHistoryCVD: true,
      smoker: false,
      physicalActivity: 'Sedentary',
    },
    alerts: [
      { id: 1, severity: 'high', title: 'Hypertensive Crisis Risk', message: 'Sustained elevated resting HR (84 bpm) combined with BP history of 165/100. Sleep quality deteriorating — only 2.5 hours of deep sleep in past 3 nights.', time: '15 min ago', action: 'Monitor BP every 2 hours. Consider emergency dose adjustment.' },
      { id: 2, severity: 'high', title: 'Kidney Function Concern', message: 'eGFR at 48 mL/min indicates Stage 3b CKD. High BP accelerating renal decline risk.', time: '4 hours ago', action: 'Nephrology consult. Review ACE-i/ARB dosing for renal protection.' },
      { id: 3, severity: 'moderate', title: 'Medication Adherence Below Target', message: 'Metoprolol adherence at 75% and Telmisartan at 76%. Sub-optimal BP control likely due to missed doses.', time: '1 day ago', action: 'Patient counseling. Consider simplifying regimen.' },
    ],
    riskFactors: [
      { name: 'Severe Hypertension', contribution: 28, color: '#ec4899' },
      { name: 'CKD Stage 3b', contribution: 20, color: '#ef4444' },
      { name: 'CAD History', contribution: 18, color: '#f43f5e' },
      { name: 'Age (65)', contribution: 12, color: '#6366f1' },
      { name: 'Poor Med Adherence', contribution: 10, color: '#f59e0b' },
      { name: 'Elevated BNP', contribution: 7, color: '#8b5cf6' },
      { name: 'Low HDL', contribution: 5, color: '#06b6d4' },
    ],
    recommendation: 'URGENT: Increase BP monitoring to every 2 hours. Schedule nephrology consult within 1 week. Consider Metoprolol dose adjustment. Simplify medication regimen to improve adherence. Refer to dietitian for renal-friendly diet.',
  },
];

// Attach generated vitals to each patient
mockPatients.forEach(p => {
  const baseHR = p.ehr.restingHR;
  const baseHRV = p.riskLevel === 'Low' ? 48 : p.riskLevel === 'Moderate' ? 38 : p.riskLevel === 'High' ? 28 : 22;
  const baseSPO2 = p.riskLevel === 'Critical' ? 96.5 : 97.5;

  p.vitals = generateVitals(baseHR, baseHRV, baseSPO2, p.riskLevel, p.eventType);
  p.dailyAggregates = generateDailyAggregates(p.vitals);
});
