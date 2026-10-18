"""
CardioTwin — Data Preprocessing & Feature Engineering
======================================================
Handles the fusion of EHR (static) and wearable (dynamic) data streams
into model-ready features for the dual-stream architecture.
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import warnings

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "generated")
SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")


def load_ehr_data():
    """Load and merge all EHR data sources."""
    patients = pd.read_csv(os.path.join(DATA_DIR, "ehr_patients.csv"))
    labs = pd.read_csv(os.path.join(DATA_DIR, "ehr_lab_results.csv"))
    diagnoses = pd.read_csv(os.path.join(DATA_DIR, "ehr_diagnoses.csv"))
    meds = pd.read_csv(os.path.join(DATA_DIR, "ehr_medications.csv"))

    return patients, labs, diagnoses, meds


def load_wearable_data():
    """Load wearable time-series data."""
    return pd.read_csv(os.path.join(DATA_DIR, "wearable_timeseries.csv"))


def engineer_static_features(patients, labs, diagnoses, meds):
    """
    Engineer features from static EHR data for the XGBoost model.
    Returns a DataFrame with one row per patient and 42 engineered features.
    """
    features = patients[["patient_id"]].copy()

    # ── Demographics ──────────────────────────────────────────────────────
    features["age"] = patients["age"]
    features["is_male"] = (patients["gender"] == "Male").astype(int)
    features["bmi"] = patients["bmi"]
    features["weight_kg"] = patients["weight_kg"]
    features["height_cm"] = patients["height_cm"]

    # ── Vitals ────────────────────────────────────────────────────────────
    features["systolic_bp"] = patients["systolic_bp"]
    features["diastolic_bp"] = patients["diastolic_bp"]
    features["pulse_pressure"] = patients["systolic_bp"] - patients["diastolic_bp"]
    features["mean_arterial_pressure"] = (
        patients["diastolic_bp"] + (patients["systolic_bp"] - patients["diastolic_bp"]) / 3
    )
    features["resting_hr"] = patients["resting_heart_rate"]

    # ── Lifestyle ─────────────────────────────────────────────────────────
    features["is_smoker"] = patients["smoker"].astype(int)
    features["alcohol_use"] = patients["alcohol_use"].astype(int)
    activity_map = {"Sedentary": 0, "Light": 1, "Moderate": 2, "Active": 3}
    features["activity_level"] = patients["physical_activity"].map(activity_map)
    features["family_history_cvd"] = patients["family_history_cvd"].astype(int)
    features["family_history_diabetes"] = patients["family_history_diabetes"].astype(int)

    # ── Lab Results (latest + aggregates) ─────────────────────────────────
    latest_labs = labs.sort_values("visit_date").groupby("patient_id").last().reset_index()
    lab_agg = labs.groupby("patient_id").agg({
        "total_cholesterol": ["mean", "std", "max"],
        "hdl": ["mean", "min"],
        "ldl": ["mean", "max"],
        "triglycerides": ["mean", "max"],
        "fasting_glucose": ["mean", "std", "max"],
        "hba1c": ["mean", "max"],
        "creatinine": ["mean", "max"],
        "egfr": ["mean", "min"],
        "crp_mg_l": ["mean", "max"],
        "bnp_pg_ml": ["mean", "max"],
        "troponin_ng_ml": ["mean", "max"],
    })
    lab_agg.columns = ["_".join(col).strip() for col in lab_agg.columns]
    lab_agg = lab_agg.reset_index()

    features = features.merge(latest_labs[["patient_id", "total_cholesterol", "hdl", "ldl",
                                            "triglycerides", "fasting_glucose", "hba1c",
                                            "creatinine", "egfr", "crp_mg_l", "bnp_pg_ml",
                                            "troponin_ng_ml", "hemoglobin_g_dl", "vitamin_d_ng_ml",
                                            "is_diabetic"]],
                              on="patient_id", how="left")

    # Rename latest lab columns
    features = features.rename(columns={
        "total_cholesterol": "latest_total_chol",
        "hdl": "latest_hdl",
        "ldl": "latest_ldl",
        "triglycerides": "latest_triglycerides",
        "fasting_glucose": "latest_fasting_glucose",
        "hba1c": "latest_hba1c",
        "creatinine": "latest_creatinine",
        "egfr": "latest_egfr",
        "crp_mg_l": "latest_crp",
        "bnp_pg_ml": "latest_bnp",
        "troponin_ng_ml": "latest_troponin",
        "hemoglobin_g_dl": "latest_hemoglobin",
        "vitamin_d_ng_ml": "latest_vitamin_d",
        "is_diabetic": "is_diabetic",
    })

    # ── Derived Risk Ratios ───────────────────────────────────────────────
    features["chol_hdl_ratio"] = features["latest_total_chol"] / features["latest_hdl"].clip(lower=1)
    features["ldl_hdl_ratio"] = features["latest_ldl"] / features["latest_hdl"].clip(lower=1)
    features["tg_hdl_ratio"] = features["latest_triglycerides"] / features["latest_hdl"].clip(lower=1)

    # ── Diagnosis Count Features ──────────────────────────────────────────
    dx_counts = diagnoses.groupby("patient_id").agg(
        num_diagnoses=("icd10_code", "nunique"),
        has_hypertension=("icd10_code", lambda x: int("I10" in x.values)),
        has_afib=("icd10_code", lambda x: int("I48.91" in x.values)),
        has_cad=("icd10_code", lambda x: int("I25.10" in x.values)),
        has_heart_failure=("icd10_code", lambda x: int("I50.9" in x.values)),
        has_ckd=("icd10_code", lambda x: int("N18.3" in x.values)),
        has_sleep_apnea=("icd10_code", lambda x: int("G47.33" in x.values)),
    ).reset_index()
    features = features.merge(dx_counts, on="patient_id", how="left")
    features["num_diagnoses"] = features["num_diagnoses"].fillna(0)

    # ── Medication Features ───────────────────────────────────────────────
    if len(meds) > 0:
        med_counts = meds.groupby("patient_id").agg(
            num_medications=("medication_name", "nunique"),
            avg_adherence=("adherence_pct", "mean"),
            on_statin=("medication_class", lambda x: int("Statin" in x.values)),
            on_beta_blocker=("medication_class", lambda x: int("Beta-blocker" in x.values)),
            on_antiplatelet=("medication_class", lambda x: int("Antiplatelet" in x.values)),
            on_anticoagulant=("medication_class", lambda x: int("Anticoagulant" in x.values)),
        ).reset_index()
        features = features.merge(med_counts, on="patient_id", how="left")
    else:
        features["num_medications"] = 0
        features["avg_adherence"] = 100
        features["on_statin"] = 0
        features["on_beta_blocker"] = 0
        features["on_antiplatelet"] = 0
        features["on_anticoagulant"] = 0

    # ── Framingham Risk Score ─────────────────────────────────────────────
    features["framingham_risk"] = patients["framingham_risk_10yr"]

    # Fill NaN
    features = features.fillna(0)

    # ── Target Variable ───────────────────────────────────────────────────
    features["cardiac_event"] = patients["cardiac_event"].astype(int)
    features["event_type"] = patients["event_type"]
    features["risk_category"] = patients["risk_category"]

    return features


def prepare_temporal_windows(wearable_df, window_hours=168, stride_hours=24):
    """Create sliding windows from wearable time-series data for LSTM input."""
    feature_cols = [
        "heart_rate", "hrv_sdnn_ms", "hrv_rmssd_ms", "spo2_pct",
        "respiratory_rate", "sleep_stage", "step_count", "skin_temp_delta_c"
    ]

    X_windows = []
    y_windows = []
    patient_ids = []

    unique_patients = wearable_df["patient_id"].unique()

    for pid in unique_patients:
        patient_data = wearable_df[wearable_df["patient_id"] == pid].sort_values("timestamp")
        values = patient_data[feature_cols].values
        labels = patient_data["is_anomaly_window"].values

        n_samples = len(values)
        if n_samples < window_hours:
            continue

        for start in range(0, n_samples - window_hours + 1, stride_hours):
            end = start + window_hours
            window = values[start:end]
            window_labels = labels[start:end]

            # Label: 1 if any part of the window contains anomaly
            label = 1 if window_labels.sum() > 0 else 0

            X_windows.append(window)
            y_windows.append(label)
            patient_ids.append(pid)

    return np.array(X_windows), np.array(y_windows), patient_ids


def prepare_training_data(test_size=0.2, val_size=0.1):
    """
    Prepare all training data for both model streams.

    Returns:
        static_data: dict with X_train, X_val, X_test, y_train, y_val, y_test
        temporal_data: dict with X_train, X_val, X_test, y_train, y_val, y_test
        scalers: fitted scalers for inference
    """
    os.makedirs(SAVED_DIR, exist_ok=True)

    print("Loading data...")
    patients, labs, diagnoses, meds = load_ehr_data()
    wearable = load_wearable_data()

    # ── Static Features ───────────────────────────────────────────────────
    print("Engineering static features...")
    static_features = engineer_static_features(patients, labs, diagnoses, meds)

    # Separate features and target
    exclude_cols = ["patient_id", "cardiac_event", "event_type", "risk_category"]
    feature_cols = [c for c in static_features.columns if c not in exclude_cols]

    X_static = static_features[feature_cols].values
    y_static = static_features["cardiac_event"].values

    # Scale
    static_scaler = StandardScaler()
    X_static_scaled = static_scaler.fit_transform(X_static)

    # Split
    X_train_s, X_temp_s, y_train_s, y_temp_s = train_test_split(
        X_static_scaled, y_static, test_size=test_size + val_size,
        random_state=42, stratify=y_static
    )
    val_ratio = val_size / (test_size + val_size)
    X_val_s, X_test_s, y_val_s, y_test_s = train_test_split(
        X_temp_s, y_temp_s, test_size=1-val_ratio,
        random_state=42, stratify=y_temp_s
    )

    static_data = {
        "X_train": X_train_s, "X_val": X_val_s, "X_test": X_test_s,
        "y_train": y_train_s, "y_val": y_val_s, "y_test": y_test_s,
        "feature_names": feature_cols,
    }

    # ── Temporal Features ─────────────────────────────────────────────────
    print("Preparing temporal windows (this may take a few minutes)...")
    X_temporal, y_temporal, temporal_pids = prepare_temporal_windows(wearable)

    # Scale temporal features per-feature
    n_windows, n_steps, n_features = X_temporal.shape
    temporal_scaler = StandardScaler()
    X_temporal_reshaped = X_temporal.reshape(-1, n_features)
    X_temporal_scaled = temporal_scaler.fit_transform(X_temporal_reshaped)
    X_temporal_scaled = X_temporal_scaled.reshape(n_windows, n_steps, n_features)

    # Split
    X_train_t, X_temp_t, y_train_t, y_temp_t = train_test_split(
        X_temporal_scaled, y_temporal, test_size=test_size + val_size,
        random_state=42, stratify=y_temporal
    )
    X_val_t, X_test_t, y_val_t, y_test_t = train_test_split(
        X_temp_t, y_temp_t, test_size=1-val_ratio,
        random_state=42, stratify=y_temp_t
    )

    temporal_data = {
        "X_train": X_train_t, "X_val": X_val_t, "X_test": X_test_t,
        "y_train": y_train_t, "y_val": y_val_t, "y_test": y_test_t,
    }

    # Save scalers
    joblib.dump(static_scaler, os.path.join(SAVED_DIR, "static_scaler.pkl"))
    joblib.dump(temporal_scaler, os.path.join(SAVED_DIR, "temporal_scaler.pkl"))

    print(f"\n📊 Data Preparation Summary:")
    print(f"  Static features: {X_static.shape[1]} features, {len(X_static)} samples")
    print(f"    Train: {len(X_train_s)} | Val: {len(X_val_s)} | Test: {len(X_test_s)}")
    print(f"    Positive rate: {y_static.mean():.2%}")
    print(f"  Temporal windows: {X_temporal.shape} (windows, timesteps, features)")
    print(f"    Train: {len(X_train_t)} | Val: {len(X_val_t)} | Test: {len(X_test_t)}")
    print(f"    Positive rate: {y_temporal.mean():.2%}")

    return static_data, temporal_data, {
        "static_scaler": static_scaler,
        "temporal_scaler": temporal_scaler,
        "feature_names": feature_cols,
    }
