"""
CardioTwin — Inference Pipeline
================================
Provides the complete prediction interface for the CardioTwin system.
"""

import os
import numpy as np
import joblib
import xgboost as xgb

SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")


class CardioTwinPredictor:
    """
    Complete inference pipeline for CardioTwin predictions.

    Usage:
        predictor = CardioTwinPredictor()
        result = predictor.predict(patient_id, ehr_features, wearable_window)
    """

    def __init__(self, temporal_model_path=None, static_model_path=None,
                 meta_model_path=None):
        """Load all trained models and scalers."""
        temporal_path = temporal_model_path or os.path.join(SAVED_DIR, "lstm_model.keras")
        static_path = static_model_path or os.path.join(SAVED_DIR, "xgboost_model.json")
        meta_path = meta_model_path or os.path.join(SAVED_DIR, "meta_learner.pkl")

        # Import tensorflow only when needed
        import tensorflow as tf

        # Load models
        self.temporal_model = tf.keras.models.load_model(
            temporal_path,
            custom_objects={"AttentionLayer": self._get_attention_layer()},
        )
        self.static_model = xgb.XGBClassifier()
        self.static_model.load_model(static_path)
        self.meta_learner = joblib.load(meta_path)

        # Load scalers
        self.static_scaler = joblib.load(os.path.join(SAVED_DIR, "static_scaler.pkl"))
        self.temporal_scaler = joblib.load(os.path.join(SAVED_DIR, "temporal_scaler.pkl"))

        print("✅ CardioTwin predictor initialized successfully")

    @staticmethod
    def _get_attention_layer():
        """Get the custom AttentionLayer class for model loading."""
        from models.temporal_model import AttentionLayer
        return AttentionLayer

    def predict(self, patient_id, ehr_features, wearable_window):
        """Run prediction for a single patient and return risk score and telemetry."""
        # Scale inputs
        ehr_scaled = self.static_scaler.transform(ehr_features.reshape(1, -1))
        wearable_reshaped = wearable_window.reshape(-1, wearable_window.shape[-1])
        wearable_scaled = self.temporal_scaler.transform(wearable_reshaped)
        wearable_scaled = wearable_scaled.reshape(1, wearable_window.shape[0], -1)

        # Individual predictions
        temporal_score = float(self.temporal_model.predict(wearable_scaled, verbose=0).flatten()[0])
        static_score = float(self.static_model.predict_proba(ehr_scaled)[:, 1][0])

        # Fusion features
        fusion_features = np.column_stack([
            [temporal_score],
            [static_score],
            [temporal_score * static_score],
            [max(temporal_score, static_score)],
            [temporal_score - static_score],
            [0.6 * temporal_score + 0.4 * static_score],
        ])

        # Fused prediction
        risk_probability = float(self.meta_learner.predict_proba(fusion_features)[:, 1][0])
        risk_score = int(risk_probability * 100)

        # Risk level
        if risk_score >= 75:
            risk_level = "Critical"
        elif risk_score >= 50:
            risk_level = "High"
        elif risk_score >= 25:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # Event type inference
        if temporal_score > static_score * 1.5:
            event_type = "Arrhythmia"
        elif static_score > temporal_score * 1.3:
            event_type = "Hypertensive Crisis"
        else:
            event_type = "Acute Coronary Syndrome"

        # Confidence
        agreement = 1.0 - abs(temporal_score - static_score)
        confidence = min(0.99, max(0.5, agreement * 0.7 + risk_probability * 0.3))

        return {
            "patient_id": patient_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "event_type": event_type,
            "confidence": round(confidence, 3),
            "temporal_score": round(temporal_score, 4),
            "static_score": round(static_score, 4),
            "fusion_score": round(risk_probability, 4),
            "recommendation": self._get_recommendation(risk_level, event_type),
        }

    @staticmethod
    def _get_recommendation(risk_level, event_type):
        """Generate clinical recommendation based on risk assessment."""
        recommendations = {
            "Critical": {
                "Arrhythmia": "URGENT: Schedule immediate Holter monitoring. Consider cardiology consult within 24 hours. Review antiarrhythmic medication dosage.",
                "Hypertensive Crisis": "URGENT: Initiate BP monitoring every 2 hours. Consider dose adjustment of antihypertensives. Assess for end-organ damage.",
                "Acute Coronary Syndrome": "EMERGENCY: Advise patient to seek immediate emergency care if chest pain develops. Pre-alert nearest cardiac care unit.",
            },
            "High": {
                "Arrhythmia": "Schedule ECG within 48 hours. Review current medications for proarrhythmic effects. Advise patient to monitor symptoms.",
                "Hypertensive Crisis": "Increase BP monitoring frequency. Review medication adherence. Schedule follow-up within 1 week.",
                "Acute Coronary Syndrome": "Order urgent lipid panel and troponin. Schedule stress test within 1 week. Review aspirin and statin therapy.",
            },
            "Moderate": {
                "default": "Continue current monitoring schedule. Reinforce lifestyle modifications. Schedule routine follow-up in 2 weeks.",
            },
            "Low": {
                "default": "Maintain current care plan. No immediate intervention needed. Next routine check in 1 month.",
            },
        }

        level_recs = recommendations.get(risk_level, recommendations["Low"])
        return level_recs.get(event_type, level_recs.get("default", "Continue routine monitoring."))
