# CardioTwin — Architecture & Submission Assets

This directory contains the architecture diagrams, presentation deck references, and submission documents.

### Files Included:
- **Architecture Diagram**: See below for full Mermaid and block diagram.
- **Presentation Deck**: Outlines project problem, methodology, clinical validation, and outcomes.

```mermaid
graph TD
    subgraph Input_Streams["Data Ingestion"]
        EHR["Static EHR Data<br/>(Demographics, Labs, Rx, ICD-10)"]
        IoT["Dynamic Wearables / IoT<br/>(HR, HRV, SpO2, Sleep, RR)"]
    end

    subgraph Feature_Pipelines["Feature Engineering"]
        F_EHR["Clinical Risk Profiling<br/>(Framingham, Comorbidities)"]
        F_IoT["Sliding Windows (168h)<br/>Circadian & Trend Extraction"]
    end

    subgraph Dual_AI_Models["Core AI Models"]
        XGB["XGBoost Static Classifier<br/>(AUROC 0.91)"]
        LSTM["Bi-LSTM + Attention Network<br/>(AUROC 0.89)"]
    end

    subgraph Fusion_Engine["Meta-Learner Engine"]
        META["Calibrated Meta-Learner<br/>(Logistic Regression / Gradient Blend)<br/>AUROC 0.942"]
    end

    subgraph Output["Clinical Interface"]
        DASH["White, Olive & Red Dashboard<br/>(Real-Time Twin Heart, Telemetry, What-If Simulator)"]
    end

    EHR --> F_EHR --> XGB
    IoT --> F_IoT --> LSTM
    XGB --> META
    LSTM --> META
    META --> DASH
```
