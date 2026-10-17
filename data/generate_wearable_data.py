"""CardioTwin — Synthetic Wearable & IoT Sensor Data Generator.
Generates hourly multi-sensor continuous telemetry (HR, HRV, SpO2, RR, Sleep, Steps, Temp).
Simulates physiological dynamics, circadian cycles, and acute cardiac event signatures.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

# ── Configuration ──────────────────────────────────────────────────────────────

SEED = 42
DAYS = 90
HOURS_PER_DAY = 24
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")

np.random.seed(SEED)


# ── Circadian Rhythm Models ───────────────────────────────────────────────────

def circadian_hr_pattern(hour, base_hr, age):
    """Generate circadian heart rate pattern with age adjustment."""
    # Resting phase: 0–6 AM, Active phase: 8 AM–9 PM
    if 0 <= hour < 6:
        # Deep rest: HR drops 15-20% below base
        phase = base_hr * (0.80 + 0.05 * np.sin(np.pi * hour / 6))
    elif 6 <= hour < 9:
        # Wake-up surge: HR increases rapidly
        t = (hour - 6) / 3
        phase = base_hr * (0.82 + 0.22 * t)
    elif 9 <= hour < 12:
        # Morning activity
        phase = base_hr * (1.0 + 0.08 * np.sin(np.pi * (hour - 9) / 3))
    elif 12 <= hour < 14:
        # Post-lunch dip
        phase = base_hr * 0.95
    elif 14 <= hour < 18:
        # Afternoon activity
        phase = base_hr * (1.02 + 0.05 * np.sin(np.pi * (hour - 14) / 4))
    elif 18 <= hour < 21:
        # Evening wind-down
        t = (hour - 18) / 3
        phase = base_hr * (1.0 - 0.08 * t)
    else:
        # Pre-sleep
        t = (hour - 21) / 3
        phase = base_hr * (0.92 - 0.10 * t)

    # Age effect: older patients have less HR variability
    age_damping = 1.0 - (age - 30) * 0.002
    noise = np.random.normal(0, 2.5 * age_damping)
    return max(40, min(150, phase + noise))


def circadian_hrv_pattern(hour, base_hrv, age):
    """Generate circadian HRV pattern (inversely related to HR)."""
    # HRV is highest during deep sleep, lowest during peak activity
    if 0 <= hour < 6:
        phase = base_hrv * 1.3
    elif 6 <= hour < 9:
        t = (hour - 6) / 3
        phase = base_hrv * (1.3 - 0.4 * t)
    elif 9 <= hour < 18:
        phase = base_hrv * (0.85 + 0.1 * np.sin(np.pi * (hour - 9) / 9))
    elif 18 <= hour < 22:
        t = (hour - 18) / 4
        phase = base_hrv * (0.9 + 0.3 * t)
    else:
        phase = base_hrv * 1.2

    # Age decline: HRV decreases ~3ms per decade
    age_factor = max(0.5, 1.0 - (age - 30) * 0.008)
    noise = np.random.normal(0, base_hrv * 0.08)
    return max(10, phase * age_factor + noise)


def generate_sleep_stage(hour):
    """Generate sleep stage based on time of day."""
    if 23 <= hour or hour < 1:
        return np.random.choice([1, 2], p=[0.6, 0.4])  # Falling asleep: light/deep
    elif 1 <= hour < 3:
        return np.random.choice([2, 3], p=[0.6, 0.4])  # Deep sleep dominant
    elif 3 <= hour < 5:
        return np.random.choice([2, 3, 1], p=[0.3, 0.4, 0.3])  # REM increases
    elif 5 <= hour < 7:
        return np.random.choice([1, 3, 0], p=[0.4, 0.3, 0.3])  # Lighter sleep, waking
    else:
        return 0  # Awake


def generate_steps(hour, activity_level):
    """Generate hourly step count based on activity level and time."""
    activity_multipliers = {"Sedentary": 0.5, "Light": 0.8, "Moderate": 1.0, "Active": 1.5}
    mult = activity_multipliers.get(activity_level, 1.0)

    if 0 <= hour < 6:
        base = 0  # Sleeping
    elif 6 <= hour < 8:
        base = np.random.poisson(200)  # Morning routine
    elif 8 <= hour < 10:
        base = np.random.poisson(800)  # Commute/morning walk
    elif 10 <= hour < 12:
        base = np.random.poisson(300)  # Office/desk
    elif 12 <= hour < 14:
        base = np.random.poisson(500)  # Lunch walk
    elif 14 <= hour < 17:
        base = np.random.poisson(250)  # Afternoon
    elif 17 <= hour < 19:
        base = np.random.poisson(900)  # Evening walk/exercise
    elif 19 <= hour < 22:
        base = np.random.poisson(200)  # Evening
    else:
        base = np.random.poisson(50)   # Pre-bed

    return max(0, int(base * mult))


# ── Cardiac Anomaly Injection ──────────────────────────────────────────────────

def inject_arrhythmia_pattern(hr, hrv_sdnn, hrv_rmssd, spo2, hours_before_event):
    """Inject gradual arrhythmia precursor patterns."""
    severity = max(0, 1.0 - hours_before_event / 48)  # Ramps up over 48 hours

    # Irregular HR with increasing variability
    hr_spike = hr + severity * np.random.choice([-20, -10, 15, 25, 35]) * np.random.random()
    # HRV becomes erratic then drops
    hrv_sdnn_mod = hrv_sdnn * (1.0 + severity * 0.5 * np.random.randn())
    hrv_rmssd_mod = hrv_rmssd * (1.0 - severity * 0.3)
    # SpO2 slight decrease
    spo2_mod = spo2 - severity * np.random.uniform(0, 3)

    return hr_spike, max(5, hrv_sdnn_mod), max(5, hrv_rmssd_mod), max(85, spo2_mod)


def inject_hypertensive_crisis_pattern(hr, hrv_sdnn, resp_rate, sleep_stage, hours_before_event):
    """Inject hypertensive crisis precursor patterns."""
    severity = max(0, 1.0 - hours_before_event / 24)  # Ramps up over 24 hours

    # Sustained elevated HR
    hr_mod = hr + severity * 15
    # HRV suppressed
    hrv_mod = hrv_sdnn * (1.0 - severity * 0.4)
    # Increased respiratory rate
    resp_mod = resp_rate + severity * 4
    # Sleep disruption
    if sleep_stage > 0 and severity > 0.5 and np.random.random() < severity:
        sleep_stage = max(0, sleep_stage - 1)  # Lighter sleep

    return hr_mod, max(10, hrv_mod), resp_mod, sleep_stage


def inject_acs_pattern(hr, hrv_sdnn, spo2, skin_temp, hours_before_event):
    """Inject Acute Coronary Syndrome precursor patterns."""
    severity = max(0, 1.0 - hours_before_event / 48)  # 48-hour ramp

    # Tachycardia
    hr_mod = hr + severity * 20 + severity * np.random.uniform(-5, 10)
    # HRV markedly decreased
    hrv_mod = hrv_sdnn * (1.0 - severity * 0.5)
    # SpO2 decrease
    spo2_mod = spo2 - severity * np.random.uniform(1, 5)
    # Skin temperature changes (cold sweats)
    skin_temp_mod = skin_temp - severity * np.random.uniform(0, 1.5)

    return hr_mod, max(8, hrv_mod), max(85, spo2_mod), skin_temp_mod


# ── Main Generator ─────────────────────────────────────────────────────────────

def generate_wearable_data():
    """Generate synthetic wearable time-series data for all patients."""
    # Load patient data
    patients_path = os.path.join(OUTPUT_DIR, "ehr_patients.csv")
    if not os.path.exists(patients_path):
        raise FileNotFoundError(
            f"EHR patient data not found at {patients_path}. "
            "Run generate_synthetic_ehr.py first."
        )

    patients_df = pd.read_csv(patients_path)
    print(f"Loaded {len(patients_df)} patients from EHR data.")

    all_records = []
    start_date = datetime(2025, 3, 1)

    limit = int(os.environ.get("MAX_PATIENTS", len(patients_df)))
    patients_subset = patients_df.head(limit)
    total_patients = len(patients_subset)
    event_patients = patients_subset[patients_subset["cardiac_event"] == True]
    print(f"Generating wearable telemetry for {total_patients} patients ({len(event_patients)} with cardiac events)")

    for idx, (_, patient) in enumerate(patients_subset.iterrows()):
        if (idx + 1) % 25 == 0:
            print(f"  Generating data for patient {idx+1}/{total_patients}...")

        pid = patient["patient_id"]
        age = patient["age"]
        base_hr = patient["resting_heart_rate"]
        bmi = patient["bmi"]
        activity_level = patient["physical_activity"]
        has_event = patient["cardiac_event"]
        event_type = patient.get("event_type", "None")

        # Patient-specific baselines
        base_hrv_sdnn = max(15, 50 - (age - 30) * 0.5 + np.random.normal(0, 8))
        base_hrv_rmssd = base_hrv_sdnn * np.random.uniform(0.7, 1.0)
        base_spo2 = np.clip(np.random.normal(97.5, 0.8), 93, 100)
        base_resp = np.clip(np.random.normal(16, 2), 12, 24)
        base_skin_temp = np.random.normal(0.0, 0.3)  # Delta from 36.6°C

        # If patient has event, place it in the last 7 days
        if has_event and event_type != "None":
            event_hour = (DAYS - np.random.randint(1, 7)) * 24 + np.random.randint(0, 24)
        else:
            event_hour = -1  # No event

        total_hours = DAYS * HOURS_PER_DAY

        for h in range(total_hours):
            current_time = start_date + timedelta(hours=h)
            hour_of_day = current_time.hour
            day_of_week = current_time.weekday()

            # Base circadian signals
            hr = circadian_hr_pattern(hour_of_day, base_hr, age)
            hrv_sdnn = circadian_hrv_pattern(hour_of_day, base_hrv_sdnn, age)
            hrv_rmssd = hrv_sdnn * np.random.uniform(0.65, 0.95)
            spo2 = np.clip(base_spo2 + np.random.normal(0, 0.3), 88, 100)
            resp_rate = base_resp + np.random.normal(0, 1)
            sleep_stage = generate_sleep_stage(hour_of_day)
            steps = generate_steps(hour_of_day, activity_level)
            skin_temp = base_skin_temp + np.random.normal(0, 0.15)

            # Weekend effect (more sedentary, different sleep)
            if day_of_week >= 5:
                if 9 <= hour_of_day <= 11:
                    hr *= 0.95  # Later wakeup
                steps = int(steps * 0.7)

            # BMI effect on baseline
            if bmi > 30:
                hr += (bmi - 30) * 0.3
                hrv_sdnn *= 0.9
                spo2 -= 0.5

            # Exercise burst (random ~30-min exercise sessions)
            if np.random.random() < 0.02 and 6 <= hour_of_day <= 20:
                hr += np.random.uniform(30, 60)
                steps += np.random.randint(2000, 5000)
                hrv_sdnn *= 0.6

            # Inject cardiac event precursors
            if event_hour > 0 and h <= event_hour:
                hours_before = event_hour - h
                if hours_before <= 48:
                    if event_type == "Arrhythmia":
                        hr, hrv_sdnn, hrv_rmssd, spo2 = inject_arrhythmia_pattern(
                            hr, hrv_sdnn, hrv_rmssd, spo2, hours_before
                        )
                    elif event_type == "Hypertensive Crisis":
                        hr, hrv_sdnn, resp_rate, sleep_stage = inject_hypertensive_crisis_pattern(
                            hr, hrv_sdnn, resp_rate, sleep_stage, hours_before
                        )
                    elif event_type == "Acute Coronary Syndrome":
                        hr, hrv_sdnn, spo2, skin_temp = inject_acs_pattern(
                            hr, hrv_sdnn, spo2, skin_temp, hours_before
                        )

            # Compute stress score (composite of HR elevation + HRV depression)
            hr_stress = max(0, (hr - base_hr) / base_hr)
            hrv_stress = max(0, (base_hrv_sdnn - hrv_sdnn) / base_hrv_sdnn)
            stress_score = np.clip((hr_stress * 0.4 + hrv_stress * 0.6) * 100, 0, 100)

            # Label: is this within the 48-hour pre-event window?
            is_anomaly_window = 0
            if event_hour > 0:
                hours_before = event_hour - h
                if 0 <= hours_before <= 48:
                    is_anomaly_window = 1

            all_records.append({
                "patient_id": pid,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "heart_rate": round(np.clip(hr, 35, 180), 1),
                "hrv_sdnn_ms": round(max(5, hrv_sdnn), 1),
                "hrv_rmssd_ms": round(max(5, hrv_rmssd), 1),
                "spo2_pct": round(np.clip(spo2, 85, 100), 1),
                "respiratory_rate": round(np.clip(resp_rate, 8, 35), 1),
                "sleep_stage": sleep_stage,
                "step_count": max(0, steps),
                "skin_temp_delta_c": round(skin_temp, 2),
                "stress_score": round(stress_score, 1),
                "is_anomaly_window": is_anomaly_window,
                "event_type": event_type if is_anomaly_window else "None",
            })

    df = pd.DataFrame(all_records)
    return df


def main():
    """Main execution for wearable data generation."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  CardioTwin — Synthetic Wearable Data Generator")
    print("=" * 60)

    print(f"\n📡 Generating {DAYS} days of hourly wearable data...\n")
    df = generate_wearable_data()

    print(f"\n📊 Dataset Summary:")
    print(f"  → Total records: {len(df):,}")
    print(f"  → Unique patients: {df['patient_id'].nunique()}")
    print(f"  → Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  → Anomaly windows: {df['is_anomaly_window'].sum():,} hours ({df['is_anomaly_window'].mean()*100:.2f}%)")

    # Feature statistics
    print(f"\n📈 Feature Statistics:")
    for col in ["heart_rate", "hrv_sdnn_ms", "spo2_pct", "respiratory_rate", "stress_score"]:
        print(f"  → {col}: mean={df[col].mean():.1f}, std={df[col].std():.1f}, "
              f"min={df[col].min():.1f}, max={df[col].max():.1f}")

    # Save
    output_path = os.path.join(OUTPUT_DIR, "wearable_timeseries.csv")
    print(f"\n💾 Saving to {output_path}...")

    # Save in chunks for large files
    df.to_csv(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  ✓ Saved ({file_size_mb:.1f} MB)")

    print(f"\n{'=' * 60}")
    print("  ✅ Wearable data generation complete!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
