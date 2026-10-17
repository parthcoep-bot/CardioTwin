"""CardioTwin — Synthetic EHR Data Generator.
Generates realistic Indian population synthetic EHR data (demographics, labs, medications, diagnoses).
All data is synthetic; no real patient data is used.
"""

import os
import sys
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import warnings

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

# ── Configuration ──────────────────────────────────────────────────────────────

NUM_PATIENTS = 1000
SEED = 42
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")

np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

# Indian-specific distributions
STATES = [
    "Karnataka", "Maharashtra", "Tamil Nadu", "Delhi", "Kerala",
    "Telangana", "West Bengal", "Gujarat", "Rajasthan", "Uttar Pradesh",
    "Madhya Pradesh", "Andhra Pradesh", "Punjab", "Haryana", "Bihar"
]

BLOOD_GROUPS = ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"]
BLOOD_GROUP_WEIGHTS = [0.22, 0.30, 0.28, 0.06, 0.05, 0.04, 0.04, 0.01]

# ICD-10 codes relevant to cardiovascular conditions
CVD_DIAGNOSES = {
    "I10": "Essential hypertension",
    "I11.9": "Hypertensive heart disease without heart failure",
    "I25.10": "Atherosclerotic heart disease",
    "I48.91": "Atrial fibrillation, unspecified",
    "I50.9": "Heart failure, unspecified",
    "E11.9": "Type 2 diabetes mellitus without complications",
    "E11.65": "Type 2 diabetes with hyperglycemia",
    "E78.5": "Dyslipidemia, unspecified",
    "E78.0": "Pure hypercholesterolemia",
    "E66.01": "Morbid obesity due to excess calories",
    "J44.1": "COPD with acute exacerbation",
    "N18.3": "Chronic kidney disease, stage 3",
    "G47.33": "Obstructive sleep apnea",
    "F17.210": "Nicotine dependence, cigarettes",
    "I63.9": "Cerebral infarction, unspecified",
}

# Common cardiac medications
MEDICATIONS = {
    "Atorvastatin": {"class": "Statin", "doses": ["10mg", "20mg", "40mg", "80mg"]},
    "Metoprolol": {"class": "Beta-blocker", "doses": ["25mg", "50mg", "100mg"]},
    "Amlodipine": {"class": "CCB", "doses": ["2.5mg", "5mg", "10mg"]},
    "Ramipril": {"class": "ACE-inhibitor", "doses": ["2.5mg", "5mg", "10mg"]},
    "Telmisartan": {"class": "ARB", "doses": ["20mg", "40mg", "80mg"]},
    "Aspirin": {"class": "Antiplatelet", "doses": ["75mg", "150mg"]},
    "Clopidogrel": {"class": "Antiplatelet", "doses": ["75mg"]},
    "Metformin": {"class": "Antidiabetic", "doses": ["500mg", "850mg", "1000mg"]},
    "Losartan": {"class": "ARB", "doses": ["25mg", "50mg", "100mg"]},
    "Furosemide": {"class": "Diuretic", "doses": ["20mg", "40mg", "80mg"]},
    "Warfarin": {"class": "Anticoagulant", "doses": ["1mg", "2mg", "5mg"]},
    "Rosuvastatin": {"class": "Statin", "doses": ["5mg", "10mg", "20mg"]},
}


# ── Helper Functions ───────────────────────────────────────────────────────────

def generate_indian_bmi(age, gender):
    """Generate BMI with Indian population distribution (higher central obesity)."""
    if gender == "Male":
        base_bmi = np.random.normal(25.5, 4.5)
    else:
        base_bmi = np.random.normal(26.2, 5.0)

    # Age-related increase
    age_factor = max(0, (age - 30) * 0.05)
    bmi = base_bmi + age_factor
    return np.clip(bmi, 16.0, 48.0)


def compute_framingham_risk(age, gender, total_chol, hdl, systolic_bp, bp_treated, smoker, diabetic):
    """Simplified Framingham 10-year CVD risk calculator."""
    risk = 0.0

    # Age contribution
    if gender == "Male":
        risk += (age - 30) * 0.8
    else:
        risk += (age - 30) * 0.6

    # Cholesterol
    risk += max(0, (total_chol - 200) * 0.05)
    risk -= max(0, (hdl - 40) * 0.1)

    # Blood pressure
    bp_factor = max(0, (systolic_bp - 120) * 0.08)
    if bp_treated:
        bp_factor *= 1.3
    risk += bp_factor

    # Smoking
    if smoker:
        risk += 8.0

    # Diabetes
    if diabetic:
        risk += 6.0 if gender == "Male" else 8.0

    return np.clip(risk, 1.0, 95.0)


def assign_risk_category(framingham, num_comorbidities, age):
    """Assign cardiovascular risk category based on multiple factors."""
    score = framingham + num_comorbidities * 3 + max(0, age - 55) * 0.5
    if score > 45:
        return "Critical"
    elif score > 30:
        return "High"
    elif score > 18:
        return "Moderate"
    else:
        return "Low"


def generate_cardiac_event(risk_category):
    """Determine if patient has a cardiac event based on risk category."""
    event_probs = {"Low": 0.03, "Moderate": 0.12, "High": 0.35, "Critical": 0.60}
    has_event = np.random.random() < event_probs[risk_category]

    if has_event:
        event_types = ["Arrhythmia", "Hypertensive Crisis", "Acute Coronary Syndrome"]
        weights = {"Low": [0.7, 0.2, 0.1], "Moderate": [0.4, 0.35, 0.25],
                   "High": [0.3, 0.3, 0.4], "Critical": [0.25, 0.25, 0.5]}
        event_type = np.random.choice(event_types, p=weights[risk_category])
        return True, event_type
    return False, None


# ── Data Generation ────────────────────────────────────────────────────────────

def generate_patients():
    """Generate synthetic patient demographics and baseline data."""
    patients = []

    for i in range(NUM_PATIENTS):
        pid = f"P{i+1:04d}"
        gender = np.random.choice(["Male", "Female"], p=[0.55, 0.45])
        age = int(np.clip(np.random.normal(52, 14), 25, 85))
        state = np.random.choice(STATES)
        blood_group = np.random.choice(BLOOD_GROUPS, p=BLOOD_GROUP_WEIGHTS)

        # Baseline vitals
        bmi = round(generate_indian_bmi(age, gender), 1)
        height_cm = round(np.random.normal(170 if gender == "Male" else 158, 7), 1)
        weight_kg = round(bmi * (height_cm / 100) ** 2, 1)

        # Lifestyle factors
        smoker = np.random.random() < (0.25 if gender == "Male" else 0.05)
        alcohol = np.random.random() < (0.30 if gender == "Male" else 0.08)
        physical_activity = np.random.choice(
            ["Sedentary", "Light", "Moderate", "Active"],
            p=[0.35, 0.30, 0.25, 0.10]
        )

        # Family history of CVD
        family_history_cvd = np.random.random() < 0.35
        family_history_diabetes = np.random.random() < 0.40

        # Baseline blood pressure (higher for Indian population)
        if age > 50:
            systolic_bp = int(np.random.normal(138, 18))
            diastolic_bp = int(np.random.normal(86, 10))
        else:
            systolic_bp = int(np.random.normal(125, 15))
            diastolic_bp = int(np.random.normal(80, 9))

        systolic_bp = np.clip(systolic_bp, 90, 200)
        diastolic_bp = np.clip(diastolic_bp, 55, 120)

        resting_hr = int(np.clip(np.random.normal(74, 10), 50, 110))

        patients.append({
            "patient_id": pid,
            "age": age,
            "gender": gender,
            "state": state,
            "blood_group": blood_group,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "systolic_bp": int(systolic_bp),
            "diastolic_bp": int(diastolic_bp),
            "resting_heart_rate": resting_hr,
            "smoker": smoker,
            "alcohol_use": alcohol,
            "physical_activity": physical_activity,
            "family_history_cvd": family_history_cvd,
            "family_history_diabetes": family_history_diabetes,
            "registration_date": fake.date_between(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2025, 12, 31)
            ).isoformat(),
        })

    return pd.DataFrame(patients)


def generate_lab_results(patients_df):
    """Generate laboratory test results for each patient."""
    labs = []
    ref_date = datetime(2025, 6, 1)

    for _, patient in patients_df.iterrows():
        pid = patient["patient_id"]
        age = patient["age"]
        bmi = patient["bmi"]
        smoker = patient["smoker"]

        # Number of lab visits (more for older/sicker patients)
        n_visits = np.random.randint(2, 8)

        for visit in range(n_visits):
            visit_date = ref_date - timedelta(days=int(np.random.uniform(0, 730)))

            # Lipid panel — Indian-specific (higher triglycerides, lower HDL)
            total_chol = round(np.random.normal(210, 40) + (bmi - 25) * 2, 1)
            hdl = round(np.random.normal(42 if patient["gender"] == "Male" else 50, 10), 1)
            ldl = round(total_chol * np.random.uniform(0.55, 0.70), 1)
            triglycerides = round(np.random.normal(170, 60) + (bmi - 25) * 5, 1)

            # Glucose metabolism
            is_diabetic = bmi > 28 and np.random.random() < 0.4
            fasting_glucose = round(np.random.normal(
                140 if is_diabetic else 95, 25 if is_diabetic else 12
            ), 1)
            hba1c = round(np.random.normal(
                7.8 if is_diabetic else 5.4, 1.0 if is_diabetic else 0.4
            ), 1)

            # Kidney function
            creatinine = round(np.random.normal(1.0 + (age - 40) * 0.005, 0.2), 2)
            egfr = round(np.clip(175 * creatinine**(-1.154) * age**(-0.203) * (0.742 if patient["gender"] == "Female" else 1), 15, 120), 1)

            # Inflammatory markers
            crp = round(np.random.exponential(2.0) + (1.5 if smoker else 0), 2)

            # Cardiac biomarkers
            bnp = round(np.random.exponential(80) + max(0, age - 60) * 5, 1)
            troponin = round(np.clip(np.random.exponential(0.01), 0, 0.5), 4)

            # Thyroid
            tsh = round(np.random.normal(2.5, 1.5), 2)

            # Hemoglobin
            hemoglobin = round(np.random.normal(
                14.0 if patient["gender"] == "Male" else 12.5, 1.5
            ), 1)

            # Vitamin D (commonly deficient in India)
            vitamin_d = round(np.random.normal(22, 10), 1)

            labs.append({
                "patient_id": pid,
                "visit_date": visit_date.strftime("%Y-%m-%d"),
                "total_cholesterol": np.clip(total_chol, 100, 400),
                "hdl": np.clip(hdl, 20, 100),
                "ldl": np.clip(ldl, 40, 250),
                "triglycerides": np.clip(triglycerides, 50, 500),
                "fasting_glucose": np.clip(fasting_glucose, 60, 350),
                "hba1c": np.clip(hba1c, 4.0, 14.0),
                "creatinine": np.clip(creatinine, 0.5, 4.0),
                "egfr": egfr,
                "crp_mg_l": np.clip(crp, 0.1, 30),
                "bnp_pg_ml": np.clip(bnp, 5, 2000),
                "troponin_ng_ml": troponin,
                "tsh_miu_l": np.clip(tsh, 0.1, 15),
                "hemoglobin_g_dl": np.clip(hemoglobin, 7, 19),
                "vitamin_d_ng_ml": np.clip(vitamin_d, 5, 80),
                "is_diabetic": is_diabetic,
            })

    return pd.DataFrame(labs)


def generate_diagnoses(patients_df, labs_df):
    """Generate ICD-10 coded diagnosis history."""
    diagnoses = []
    ref_date = datetime(2025, 6, 1)

    for _, patient in patients_df.iterrows():
        pid = patient["patient_id"]
        age = patient["age"]
        bmi = patient["bmi"]
        smoker = patient["smoker"]

        patient_labs = labs_df[labs_df["patient_id"] == pid]
        has_diabetes = patient_labs["is_diabetic"].any() if len(patient_labs) > 0 else False

        # Determine diagnoses based on risk factors
        patient_diagnoses = []

        # Hypertension
        if patient["systolic_bp"] > 140 or patient["diastolic_bp"] > 90:
            patient_diagnoses.append("I10")
            if np.random.random() < 0.15:
                patient_diagnoses.append("I11.9")

        # Diabetes
        if has_diabetes:
            patient_diagnoses.append("E11.9")
            if np.random.random() < 0.3:
                patient_diagnoses.append("E11.65")

        # Dyslipidemia
        if len(patient_labs) > 0 and patient_labs["total_cholesterol"].mean() > 240:
            patient_diagnoses.append("E78.5")
            if patient_labs["ldl"].mean() > 160:
                patient_diagnoses.append("E78.0")

        # Obesity
        if bmi > 35:
            patient_diagnoses.append("E66.01")

        # Smoking
        if smoker:
            patient_diagnoses.append("F17.210")
            if age > 50 and np.random.random() < 0.2:
                patient_diagnoses.append("J44.1")

        # Atrial fibrillation (age-related)
        if age > 60 and np.random.random() < 0.12:
            patient_diagnoses.append("I48.91")

        # CAD (based on age + risk factors)
        if age > 50 and len(patient_diagnoses) >= 2 and np.random.random() < 0.15:
            patient_diagnoses.append("I25.10")

        # Heart failure
        if age > 65 and len(patient_diagnoses) >= 3 and np.random.random() < 0.08:
            patient_diagnoses.append("I50.9")

        # CKD
        if len(patient_labs) > 0 and patient_labs["egfr"].mean() < 60:
            patient_diagnoses.append("N18.3")

        # Sleep apnea (obesity-related)
        if bmi > 30 and np.random.random() < 0.25:
            patient_diagnoses.append("G47.33")

        # Stroke history
        if age > 60 and len(patient_diagnoses) >= 3 and np.random.random() < 0.05:
            patient_diagnoses.append("I63.9")

        for icd_code in patient_diagnoses:
            diagnosis_date = ref_date - timedelta(days=int(np.random.uniform(30, 1825)))
            diagnoses.append({
                "patient_id": pid,
                "icd10_code": icd_code,
                "description": CVD_DIAGNOSES[icd_code],
                "diagnosis_date": diagnosis_date.strftime("%Y-%m-%d"),
                "status": np.random.choice(["Active", "Resolved"], p=[0.85, 0.15]),
            })

    return pd.DataFrame(diagnoses)


def generate_medications(patients_df, diagnoses_df):
    """Generate medication history based on diagnoses."""
    meds = []

    for _, patient in patients_df.iterrows():
        pid = patient["patient_id"]
        patient_dx = diagnoses_df[diagnoses_df["patient_id"] == pid]

        if len(patient_dx) == 0:
            continue

        icd_codes = set(patient_dx["icd10_code"].values)
        patient_meds = []

        # Hypertension meds
        if "I10" in icd_codes or "I11.9" in icd_codes:
            bp_meds = np.random.choice(["Amlodipine", "Ramipril", "Telmisartan", "Losartan", "Metoprolol"],
                                        size=np.random.randint(1, 3), replace=False)
            patient_meds.extend(bp_meds)

        # Statin therapy
        if "E78.5" in icd_codes or "E78.0" in icd_codes or "I25.10" in icd_codes:
            statin = np.random.choice(["Atorvastatin", "Rosuvastatin"])
            patient_meds.append(statin)

        # Antiplatelet
        if "I25.10" in icd_codes or "I63.9" in icd_codes:
            patient_meds.append("Aspirin")
            if np.random.random() < 0.4:
                patient_meds.append("Clopidogrel")

        # Diabetes meds
        if "E11.9" in icd_codes or "E11.65" in icd_codes:
            patient_meds.append("Metformin")

        # Heart failure
        if "I50.9" in icd_codes:
            patient_meds.append("Furosemide")
            if "Metoprolol" not in patient_meds:
                patient_meds.append("Metoprolol")

        # AFib
        if "I48.91" in icd_codes:
            patient_meds.append("Warfarin")
            if "Metoprolol" not in patient_meds:
                patient_meds.append("Metoprolol")

        for med_name in set(patient_meds):
            if med_name in MEDICATIONS:
                med_info = MEDICATIONS[med_name]
                start_date = datetime(2024, 1, 1) + timedelta(days=int(np.random.uniform(0, 545)))
                adherence = round(np.random.beta(8, 2) * 100, 1)  # Most patients have decent adherence

                meds.append({
                    "patient_id": pid,
                    "medication_name": med_name,
                    "medication_class": med_info["class"],
                    "dose": np.random.choice(med_info["doses"]),
                    "frequency": np.random.choice(["Once daily", "Twice daily"], p=[0.7, 0.3]),
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "active": np.random.choice([True, False], p=[0.90, 0.10]),
                    "adherence_pct": adherence,
                })

    return pd.DataFrame(meds)


def add_risk_labels(patients_df, labs_df, diagnoses_df):
    """Add cardiovascular risk labels for model training."""
    risk_data = []

    for _, patient in patients_df.iterrows():
        pid = patient["patient_id"]
        age = patient["age"]
        bmi = patient["bmi"]

        patient_labs = labs_df[labs_df["patient_id"] == pid]
        patient_dx = diagnoses_df[diagnoses_df["patient_id"] == pid]
        num_comorbidities = len(patient_dx["icd10_code"].unique()) if len(patient_dx) > 0 else 0

        # Get latest lab values
        if len(patient_labs) > 0:
            latest_labs = patient_labs.sort_values("visit_date").iloc[-1]
            total_chol = latest_labs["total_cholesterol"]
            hdl = latest_labs["hdl"]
            is_diabetic = latest_labs["is_diabetic"]
        else:
            total_chol = 200
            hdl = 45
            is_diabetic = False

        bp_treated = num_comorbidities > 0 and patient["systolic_bp"] > 130

        # Framingham risk
        framingham = compute_framingham_risk(
            age, patient["gender"], total_chol, hdl,
            patient["systolic_bp"], bp_treated, patient["smoker"], is_diabetic
        )

        risk_category = assign_risk_category(framingham, num_comorbidities, age)
        has_event, event_type = generate_cardiac_event(risk_category)

        risk_data.append({
            "patient_id": pid,
            "framingham_risk_10yr": round(framingham, 1),
            "num_comorbidities": num_comorbidities,
            "risk_category": risk_category,
            "cardiac_event": has_event,
            "event_type": event_type if event_type else "None",
        })

    risk_df = pd.DataFrame(risk_data)
    return patients_df.merge(risk_df, on="patient_id")


# ── Main Execution ─────────────────────────────────────────────────────────────

def main():
    """Generate all synthetic EHR datasets."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  CardioTwin — Synthetic EHR Data Generator")
    print("=" * 60)

    # Step 1: Generate patients
    print(f"\n[1/5] Generating {NUM_PATIENTS} synthetic patients...")
    patients_df = generate_patients()
    print(f"  ✓ {len(patients_df)} patients generated")
    print(f"  → Age range: {patients_df['age'].min()}–{patients_df['age'].max()} years")
    print(f"  → Gender: {(patients_df['gender']=='Male').sum()} M / {(patients_df['gender']=='Female').sum()} F")

    # Step 2: Generate lab results
    print(f"\n[2/5] Generating laboratory results...")
    labs_df = generate_lab_results(patients_df)
    print(f"  ✓ {len(labs_df)} lab records generated")
    print(f"  → Avg visits per patient: {len(labs_df)/NUM_PATIENTS:.1f}")

    # Step 3: Generate diagnoses
    print(f"\n[3/5] Generating diagnosis records...")
    diagnoses_df = generate_diagnoses(patients_df, labs_df)
    print(f"  ✓ {len(diagnoses_df)} diagnosis records generated")
    print(f"  → Unique ICD-10 codes: {diagnoses_df['icd10_code'].nunique()}")

    # Step 4: Generate medications
    print(f"\n[4/5] Generating medication records...")
    meds_df = generate_medications(patients_df, diagnoses_df)
    print(f"  ✓ {len(meds_df)} medication records generated")

    # Step 5: Add risk labels
    print(f"\n[5/5] Computing risk categories and event labels...")
    patients_df = add_risk_labels(patients_df, labs_df, diagnoses_df)

    risk_dist = patients_df["risk_category"].value_counts()
    event_dist = patients_df["cardiac_event"].value_counts()
    print(f"  ✓ Risk distribution:")
    for cat in ["Low", "Moderate", "High", "Critical"]:
        if cat in risk_dist.index:
            print(f"    • {cat}: {risk_dist[cat]} ({risk_dist[cat]/NUM_PATIENTS*100:.1f}%)")
    print(f"  ✓ Cardiac events: {event_dist.get(True, 0)} positive ({event_dist.get(True, 0)/NUM_PATIENTS*100:.1f}%)")

    if True in event_dist.index:
        event_types = patients_df[patients_df["cardiac_event"]]["event_type"].value_counts()
        for etype, count in event_types.items():
            print(f"    • {etype}: {count}")

    # Save to CSV
    print(f"\n💾 Saving datasets to {OUTPUT_DIR}/")
    patients_df.to_csv(os.path.join(OUTPUT_DIR, "ehr_patients.csv"), index=False)
    labs_df.to_csv(os.path.join(OUTPUT_DIR, "ehr_lab_results.csv"), index=False)
    diagnoses_df.to_csv(os.path.join(OUTPUT_DIR, "ehr_diagnoses.csv"), index=False)
    meds_df.to_csv(os.path.join(OUTPUT_DIR, "ehr_medications.csv"), index=False)

    print(f"  ✓ ehr_patients.csv        ({len(patients_df)} rows)")
    print(f"  ✓ ehr_lab_results.csv      ({len(labs_df)} rows)")
    print(f"  ✓ ehr_diagnoses.csv        ({len(diagnoses_df)} rows)")
    print(f"  ✓ ehr_medications.csv      ({len(meds_df)} rows)")

    print(f"\n{'=' * 60}")
    print("  ✅ Synthetic EHR generation complete!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
