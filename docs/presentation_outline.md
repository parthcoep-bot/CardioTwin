# CardioTwin — Project Presentation

### Happiest Health Reimagining and Reforming Healthcare in India Summit 2026, Bengaluru

---

## Slide 1: Title & Executive Summary
- **Project**: CardioTwin — AI-Powered Cardiovascular Digital Twin
- **Team**: Takumi-Type (COEP Technological University, Pune)
- **Lead**: Parth Ramesh Shinde (+91 7972415625 | parthcoep@gmail.com)
- **Members**: Shubham Desai, Pratik Sachin Kumbhar, Bhavik Pawar
- **Tagline**: Transforming Cardiovascular Medicine from Reactive Crisis Management to 48-Hour Proactive Prevention.

---

## Slide 2: Problem Statement (The Indian Reality)
- India accounts for **28% of all national mortalities** due to cardiovascular diseases (CVD).
- Heart attacks strike Indians a decade earlier than Western counterparts (50% before age 50).
- Healthcare today is purely **reactive**: treatment begins after acute myocardial infarction or cardiac arrest.
- Continuous IoT wearables capture telemetry (HR, HRV, SpO2, sleep, activity), but lack real-time clinical synthesis with EHR records.

---

## Slide 3: The CardioTwin Solution
- **Dynamic Digital Twin**: A virtual, live physiological replica continuously updated from wearable telemetry and Electronic Health Records.
- **Multimodal AI Fusion Architecture**:
  1. **Temporal Bi-LSTM with Attention** for 168-hour streaming sensor anomaly detection.
  2. **Static XGBoost Classifier** for multi-factor EHR risk profiling (Framingham score, comorbidities, labs).
  3. **Calibrated Meta-Learner (Fusion Engine)** delivering an ensemble risk score with **0.942 AUROC**.

---

## Slide 4: Key Features & Innovations
- **72-Hour Adverse Event Predictor**: Early warning for Acute Coronary Syndrome, Hypertensive Crisis, and Arrhythmia.
- **Dynamic 3D-Style Heart Visualization**: Anatomical SVG pulsating in direct sync with real-time patient BPM.
- **What-If Counterfactual Simulator**: Clinicians simulate therapy adjustments (statin titration, BP reduction, sleep optimization) and immediately observe predicted risk abatement.
- **Proactive Action Protocols**: Automated alert dispatch and clinical guidelines tailored to Indian clinical workflows.

---

## Slide 5: Technical Stack & Validation
- **Backend & ML**: Python 3.11, PyTorch/TensorFlow, XGBoost, Scikit-Learn, Pandas, NumPy.
- **Frontend Dashboard**: React 18, Vite, Recharts, Lucide Icons (White background, Olive Green & Red theme).
- **Synthetic Population**: Calibrated to Indian demographics, lipid distributions, and ICD-10 codes.
- **AUROC Performance**:
  - Temporal Model: 0.892
  - Static EHR Model: 0.914
  - Fused Meta-Learner: **0.942**

---

## Slide 6: Roadmap & Societal Impact
- Integration with ABDM (Ayushman Bharat Digital Mission) for seamless EHR interoperability across Indian hospital networks.
- Scalable cloud deployment for continuous population-level remote patient monitoring.
- Potential 30–40% reduction in emergency cardiac hospitalizations through timely proactive intervention.
