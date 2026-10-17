# CardioTwin — Data Directory
# This directory is for data documentation. Generated data lives in ./generated/

## Data Sources (All Synthetic/Open-Source)

### 1. Electronic Health Records (EHR)
- **Generator**: `generate_synthetic_ehr.py`
- **Methodology**: Inspired by [Synthea™](https://synthetichealth.github.io/synthea/) patient generation
- **Indian-specific**: Demographics, disease prevalence, and lab value distributions calibrated to Indian population data
- **Files produced**:
  - `ehr_patients.csv` — Demographics, vitals, lifestyle, risk labels
  - `ehr_lab_results.csv` — Lipid panel, glucose, cardiac biomarkers, kidney function
  - `ehr_diagnoses.csv` — ICD-10 coded diagnoses
  - `ehr_medications.csv` — Prescription history with adherence scores

### 2. Wearable Sensor Data
- **Generator**: `generate_wearable_data.py`
- **Methodology**: Circadian rhythm modeling with realistic anomaly injection
- **Mimics**: Apple Watch, Fitbit, Google Pixel Watch sensor outputs
- **Files produced**:
  - `wearable_timeseries.csv` — Hourly readings (HR, HRV, SpO2, sleep, steps, skin temp)

### Privacy Compliance
- ✅ All data is 100% synthetic — no real patient data is used
- ✅ Compliant with DPDP Act (India) and HIPAA guidelines
- ✅ Suitable for academic research and hackathon submissions
