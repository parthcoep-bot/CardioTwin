"""CardioTwin — End-to-End Training Pipeline.
Orchestrates data checks, feature engineering, and training of temporal, static, and fusion models.
"""

import os
import sys
import time
import json
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.preprocessing import prepare_training_data
from models.temporal_model import train_temporal_model
from models.static_model import train_static_model
from models.fusion_model import train_fusion_model

SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "generated")


def check_data_exists():
    """Verify that synthetic data has been generated."""
    required_files = [
        "ehr_patients.csv",
        "ehr_lab_results.csv",
        "ehr_diagnoses.csv",
        "ehr_medications.csv",
        "wearable_timeseries.csv",
    ]

    missing = [f for f in required_files if not os.path.exists(os.path.join(DATA_DIR, f))]

    if missing:
        print("❌ Missing data files:")
        for f in missing:
            print(f"   • {f}")
        print("\n📝 Run the data generators first:")
        print("   python data/generate_synthetic_ehr.py")
        print("   python data/generate_wearable_data.py")
        return False

    return True


def main():
    """Run the complete training pipeline."""
    start_time = time.time()

    print("=" * 70)
    print("  CardioTwin — Complete Training Pipeline")
    print("  AI-Powered Cardiovascular Digital Twin")
    print("=" * 70)

    # Step 0: Check data
    print("\n[0/5] Checking data availability...")
    if not check_data_exists():
        sys.exit(1)
    print("  ✓ All data files found")

    # Step 1: Prepare training data
    print("\n" + "─" * 70)
    print("[1/5] Preparing training data...")
    print("─" * 70)
    static_data, temporal_data, scalers = prepare_training_data()

    # Step 2: Train temporal model
    print("\n" + "─" * 70)
    print("[2/5] Training Temporal Model (Bi-LSTM with Attention)...")
    print("─" * 70)
    temporal_model, temporal_history = train_temporal_model(temporal_data, epochs=50, batch_size=32)

    # Step 3: Train static model
    print("\n" + "─" * 70)
    print("[3/5] Training Static Model (XGBoost)...")
    print("─" * 70)
    static_model, static_metrics = train_static_model(static_data)

    # Step 4: Train fusion model
    print("\n" + "─" * 70)
    print("[4/5] Training Fusion Model (Meta-Learner)...")
    print("─" * 70)
    meta_learner, fusion_metrics = train_fusion_model(
        temporal_model, static_model, temporal_data, static_data
    )

    # Step 5: Final report
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("[5/5] Training Complete — Final Report")
    print("=" * 70)

    print(f"\n⏱️  Total training time: {elapsed/60:.1f} minutes")
    print(f"\n📊 Final Model Performance:")
    print(f"  {'Model':<30} {'AUROC':>10}")
    print(f"  {'─'*42}")
    print(f"  {'Temporal (Bi-LSTM + Attention)':<30} {fusion_metrics['temporal_auroc']:>10.4f}")
    print(f"  {'Static (XGBoost)':<30} {fusion_metrics['static_auroc']:>10.4f}")
    print(f"  {'Fused (Meta-Learner)':<30} {fusion_metrics['fusion_auroc']:>10.4f}")
    print(f"  {'Fused F1 Score':<30} {fusion_metrics['fusion_f1']:>10.4f}")

    # Save metrics report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_time_minutes": round(elapsed / 60, 1),
        "metrics": {
            "temporal_auroc": round(fusion_metrics["temporal_auroc"], 4),
            "static_auroc": round(fusion_metrics["static_auroc"], 4),
            "static_val_auroc": round(static_metrics["val_auroc"], 4),
            "fusion_auroc": round(fusion_metrics["fusion_auroc"], 4),
            "fusion_f1": round(fusion_metrics["fusion_f1"], 4),
        },
        "model_files": {
            "temporal": "lstm_model.keras",
            "static": "xgboost_model.json",
            "meta_learner": "meta_learner.pkl",
            "static_scaler": "static_scaler.pkl",
            "temporal_scaler": "temporal_scaler.pkl",
        }
    }

    report_path = os.path.join(SAVED_DIR, "training_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Saved Artifacts:")
    print(f"  → {SAVED_DIR}/lstm_model.keras")
    print(f"  → {SAVED_DIR}/xgboost_model.json")
    print(f"  → {SAVED_DIR}/meta_learner.pkl")
    print(f"  → {SAVED_DIR}/static_scaler.pkl")
    print(f"  → {SAVED_DIR}/temporal_scaler.pkl")
    print(f"  → {SAVED_DIR}/training_report.json")
    print(f"  → {SAVED_DIR}/*.png (training plots)")

    print(f"\n{'=' * 70}")
    print("  ✅ CardioTwin training pipeline complete!")
    print("  Next: Run the dashboard with 'cd dashboard && npm run dev'")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
