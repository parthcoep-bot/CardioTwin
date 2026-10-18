"""
CardioTwin — Fusion Model (Meta-Learner)
=========================================
Combines predictions from the temporal (LSTM) and static (XGBoost) models
through a stacking ensemble with Platt-scaled probability calibration.
"""

import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, classification_report, f1_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib

SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")


def build_fusion_model():
    """
    Build the meta-learner for fusing temporal and static predictions.

    Uses logistic regression with Platt scaling for calibrated probabilities.

    Returns:
        Calibrated logistic regression model
    """
    base_model = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=1000,
        random_state=42
    )
    return base_model


def create_fusion_features(temporal_scores, static_scores):
    """Create feature matrix for the meta-learner from temporal and static scores."""
    temporal = temporal_scores.flatten()
    static = static_scores.flatten()

    features = np.column_stack([
        temporal,
        static,
        temporal * static,                        # Interaction
        np.maximum(temporal, static),              # Max
        temporal - static,                         # Difference
        0.6 * temporal + 0.4 * static,            # Weighted average
    ])

    return features


def train_fusion_model(temporal_model, static_model, temporal_data, static_data):
    """Train the fusion meta-learner using predictions from both base models."""
    os.makedirs(SAVED_DIR, exist_ok=True)

    print(f"\n🔗 Building Fusion Model (Meta-Learner)")

    # Generate base model predictions on validation set
    print("  Generating base model predictions...")

    # Temporal predictions
    temporal_val_pred = temporal_model.predict(temporal_data["X_val"]).flatten()
    temporal_test_pred = temporal_model.predict(temporal_data["X_test"]).flatten()

    # Static predictions
    static_val_pred = static_model.predict_proba(static_data["X_val"])[:, 1]
    static_test_pred = static_model.predict_proba(static_data["X_test"])[:, 1]

    # Align sizes (use minimum overlapping set)
    min_val = min(len(temporal_val_pred), len(static_val_pred))
    min_test = min(len(temporal_test_pred), len(static_test_pred))

    temporal_val_pred = temporal_val_pred[:min_val]
    static_val_pred = static_val_pred[:min_val]
    y_val = temporal_data["y_val"][:min_val]

    temporal_test_pred = temporal_test_pred[:min_test]
    static_test_pred = static_test_pred[:min_test]
    y_test = temporal_data["y_test"][:min_test]

    # Create fusion features
    X_fusion_val = create_fusion_features(temporal_val_pred, static_val_pred)
    X_fusion_test = create_fusion_features(temporal_test_pred, static_test_pred)

    print(f"  Fusion features shape: {X_fusion_val.shape}")

    # Train meta-learner with calibration
    print("  Training meta-learner with Platt calibration...")
    base_model = build_fusion_model()

    # Fit calibrated model
    calibrated_model = CalibratedClassifierCV(
        base_model, cv=3, method="sigmoid"  # Platt scaling
    )
    calibrated_model.fit(X_fusion_val, y_val)

    # Evaluate on test set
    fusion_pred_proba = calibrated_model.predict_proba(X_fusion_test)[:, 1]
    fusion_pred_class = calibrated_model.predict(X_fusion_test)

    fusion_auroc = roc_auc_score(y_test, fusion_pred_proba)
    fusion_f1 = f1_score(y_test, fusion_pred_class)

    print(f"\n📈 Fusion Model Results:")
    print(f"  Fused AUROC: {fusion_auroc:.4f}")
    print(f"  Fused F1: {fusion_f1:.4f}")

    # Compare with individual models
    temporal_auroc = roc_auc_score(y_test, temporal_test_pred)
    static_auroc = roc_auc_score(y_test, static_test_pred)

    print(f"\n  Model Comparison:")
    print(f"  {'Model':<25} {'AUROC':>8}")
    print(f"  {'─'*35}")
    print(f"  {'Temporal (LSTM)':<25} {temporal_auroc:>8.4f}")
    print(f"  {'Static (XGBoost)':<25} {static_auroc:>8.4f}")
    print(f"  {'Fused (Meta-Learner)':<25} {fusion_auroc:>8.4f} {'✨' if fusion_auroc > max(temporal_auroc, static_auroc) else ''}")

    print(f"\n  Classification Report (Fused):")
    print(classification_report(y_test, fusion_pred_class, target_names=["No Event", "Cardiac Event"]))

    # Save
    meta_path = os.path.join(SAVED_DIR, "meta_learner.pkl")
    joblib.dump(calibrated_model, meta_path)
    print(f"  ✓ Meta-learner saved to {meta_path}")

    # Plot comparison
    plot_model_comparison(temporal_auroc, static_auroc, fusion_auroc)
    plot_risk_distribution(fusion_pred_proba, y_test)

    metrics = {
        "temporal_auroc": temporal_auroc,
        "static_auroc": static_auroc,
        "fusion_auroc": fusion_auroc,
        "fusion_f1": fusion_f1,
    }

    return calibrated_model, metrics


def plot_model_comparison(temporal_auroc, static_auroc, fusion_auroc):
    """Plot AUROC comparison bar chart."""
    models = ["Temporal\n(Bi-LSTM)", "Static\n(XGBoost)", "Fused\n(Meta-Learner)"]
    scores = [temporal_auroc, static_auroc, fusion_auroc]
    colors = ["#4C72B0", "#55A868", "#C44E52"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(models, scores, color=colors, edgecolor="white", linewidth=1.5, width=0.6)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{score:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=12)

    ax.set_ylim(0, 1.05)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("Model Performance Comparison — CardioTwin", fontsize=14, fontweight="bold")
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Random baseline")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(SAVED_DIR, "model_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Model comparison plot saved")


def plot_risk_distribution(predictions, labels):
    """Plot risk score distribution by event status."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(predictions[labels == 0], bins=40, alpha=0.7, color="#4C72B0",
            label="No Event", density=True, edgecolor="white")
    ax.hist(predictions[labels == 1], bins=40, alpha=0.7, color="#C44E52",
            label="Cardiac Event", density=True, edgecolor="white")

    ax.set_xlabel("Fused Risk Score", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title("Risk Score Distribution by Event Status", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(SAVED_DIR, "risk_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Risk distribution plot saved")


def predict_risk(temporal_model, static_model, meta_learner,
                 wearable_window, ehr_features):
    """Run full inference pipeline for a single patient."""
    # Get individual predictions
    temporal_score = temporal_model.predict(wearable_window).flatten()[0]
    static_score = static_model.predict_proba(ehr_features)[:, 1][0]

    # Create fusion features
    fusion_features = create_fusion_features(
        np.array([temporal_score]),
        np.array([static_score])
    )

    # Get fused prediction
    risk_probability = meta_learner.predict_proba(fusion_features)[:, 1][0]
    risk_score = int(risk_probability * 100)

    # Determine risk level
    if risk_score >= 75:
        risk_level = "Critical"
    elif risk_score >= 50:
        risk_level = "High"
    elif risk_score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # Determine likely event type based on temporal patterns
    if temporal_score > static_score * 1.5:
        likely_event = "Arrhythmia"
    elif static_score > temporal_score * 1.3:
        likely_event = "Hypertensive Crisis"
    else:
        likely_event = "Acute Coronary Syndrome"

    # Confidence based on model agreement
    agreement = 1.0 - abs(temporal_score - static_score)
    confidence = min(0.99, max(0.5, agreement * 0.7 + risk_probability * 0.3))

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "event_type": likely_event,
        "confidence": round(confidence, 3),
        "temporal_score": round(temporal_score, 4),
        "static_score": round(static_score, 4),
        "fusion_score": round(risk_probability, 4),
    }
