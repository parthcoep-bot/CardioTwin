"""
CardioTwin — Static Model (XGBoost)
====================================
Processes Electronic Health Record (EHR) tabular data through an XGBoost
gradient boosting classifier to compute static cardiovascular risk scores.
"""

import os
import numpy as np
import xgboost as xgb
from sklearn.metrics import (
    roc_auc_score, classification_report, precision_recall_curve,
    average_precision_score, confusion_matrix
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")


def build_static_model(scale_pos_weight=1.0):
    """
    Build XGBoost classifier for static EHR risk scoring.

    Args:
        scale_pos_weight: Weight for positive class (handles imbalance)

    Returns:
        XGBoost classifier instance
    """
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=scale_pos_weight,
        objective="binary:logistic",
        eval_metric="auc",
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )
    return model


def train_static_model(static_data):
    """
    Train XGBoost model on static EHR features.

    Args:
        static_data: dict with X_train, X_val, X_test, y_train, y_val, y_test, feature_names

    Returns:
        Trained model and evaluation metrics
    """
    os.makedirs(SAVED_DIR, exist_ok=True)

    X_train = static_data["X_train"]
    X_val = static_data["X_val"]
    X_test = static_data["X_test"]
    y_train = static_data["y_train"]
    y_val = static_data["y_val"]
    y_test = static_data["y_test"]
    feature_names = static_data["feature_names"]

    # Compute class weight
    n_pos = y_train.sum()
    n_neg = len(y_train) - n_pos
    scale_pos_weight = max(1.0, n_neg / max(n_pos, 1))

    print(f"\n📊 Building Static Model (XGBoost)")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Validation samples: {len(X_val)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  Features: {len(feature_names)}")
    print(f"  Positive rate: {y_train.mean():.2%}")
    print(f"  Scale pos weight: {scale_pos_weight:.2f}")

    model = build_static_model(scale_pos_weight)

    # Train with early stopping
    print(f"\n🏋️ Training XGBoost...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=50,
    )

    # Evaluate
    print(f"\n📈 Evaluation Results:")

    # Validation metrics
    y_val_pred = model.predict_proba(X_val)[:, 1]
    val_auroc = roc_auc_score(y_val, y_val_pred)
    val_auprc = average_precision_score(y_val, y_val_pred)
    print(f"  Validation AUROC: {val_auroc:.4f}")
    print(f"  Validation AUPRC: {val_auprc:.4f}")

    # Test metrics
    y_test_pred = model.predict_proba(X_test)[:, 1]
    y_test_class = model.predict(X_test)
    test_auroc = roc_auc_score(y_test, y_test_pred)
    test_auprc = average_precision_score(y_test, y_test_pred)
    print(f"  Test AUROC: {test_auroc:.4f}")
    print(f"  Test AUPRC: {test_auprc:.4f}")
    print(f"\n  Classification Report (Test):")
    print(classification_report(y_test, y_test_class, target_names=["No Event", "Cardiac Event"]))

    # Save model
    model_path = os.path.join(SAVED_DIR, "xgboost_model.json")
    model.save_model(model_path)
    print(f"  ✓ Model saved to {model_path}")

    # Plot feature importance
    plot_feature_importance(model, feature_names)
    plot_confusion_matrix(y_test, y_test_class)

    metrics = {
        "val_auroc": val_auroc,
        "val_auprc": val_auprc,
        "test_auroc": test_auroc,
        "test_auprc": test_auprc,
    }

    return model, metrics


def plot_feature_importance(model, feature_names, top_n=20):
    """Plot and save top feature importances."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[-top_n:]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(indices)), importances[indices], color="#4C72B0", edgecolor="white")
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices], fontsize=9)
    ax.set_xlabel("Feature Importance (Gain)", fontsize=11)
    ax.set_title("Top 20 Features — XGBoost Static Risk Model", fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(SAVED_DIR, "feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Feature importance plot saved")


def plot_confusion_matrix(y_true, y_pred):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["No Event", "Cardiac Event"],
                yticklabels=["No Event", "Cardiac Event"],
                ax=ax, linewidths=0.5, linecolor="white")
    ax.set_xlabel("Predicted", fontsize=11)
    ax.set_ylabel("Actual", fontsize=11)
    ax.set_title("Confusion Matrix — Static Model", fontsize=13, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(SAVED_DIR, "confusion_matrix_static.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Confusion matrix saved")
