# ML Models - ESI Prediction

Machine learning pipeline for predicting Emergency Severity Index (ESI) levels (1-5) from FHIR R4 patient data. Uses only features available at patient arrival to avoid temporal leakage.

## Performance

| Model | Accuracy | F1-Score |
|-------|----------|----------|
| **XGBoost** | **86.96%** | **87.23%** |
| Random Forest | 78.26% | 75.47% |
| Logistic Regression | 73.91% | 79.61% |
| LightGBM | 60.87% | 60.50% |

## Pipeline

```
FHIR Bundles (111 patients)
    │
    ▼
[1] Preprocessing (data/preprocessor_v2.py)
    Extract 23 triage-time features:
    demographics, chief complaint (SNOMED), initial vitals, patient history
    │
    ▼
[2] Labeling (data/label_generator_v2.py)
    Map SNOMED codes → ESI levels (1-5)
    Refine with vital signs
    │
    ▼
[3] Feature Engineering (data/feature_engineering_v2.py)
    One-hot encode SNOMED codes + race
    Handle missing values, train/val/test split (60/20/20)
    43 features total
    │
    ▼
[4] Model Training (baseline/train_clean_models.py)
    Train XGBoost, Random Forest, LightGBM, Logistic Regression
    class_weight='balanced' for imbalance handling
```

## Quick Start

```bash
cd models

# Install dependencies
pip install xgboost lightgbm scikit-learn pandas pyarrow imbalanced-learn

# Run full pipeline
cd data
python preprocessor_v2.py         # Step 1: Extract features
python label_generator_v2.py      # Step 2: Generate ESI labels
python feature_engineering_v2.py  # Step 3: Prepare ML data

cd ../baseline
python train_clean_models.py      # Step 4: Train models
```

## Using the Trained Model

```python
import joblib
import pandas as pd

model = joblib.load('baseline/xgboost_v2.pkl')
X_test = pd.read_parquet('data/X_test.parquet')

predictions = model.predict(X_test) + 1  # XGBoost uses 0-indexed labels
probabilities = model.predict_proba(X_test)
```

## Features (23 raw, 43 after encoding)

**Demographics:** age, gender, race

**Chief Complaint:** SNOMED code from `Encounter.reasonCode` (26 mapped codes)

**Initial Vitals:** First HR, SpO2, BP (systolic/diastolic), temperature, respiratory rate

**Patient History:** Prior encounters (total, emergency, ambulatory), days since last encounter

**Temporal:** hour of day, day of week, is weekend

## Key Design Decisions

- **SNOMED-based labeling** instead of formula-based scoring (avoids circular reasoning)
- **No encounter.class as feature** (it's the outcome we're predicting)
- **Current encounter excluded** from history counts (avoids temporal leakage)
- **First vitals only** (not latest, which could be post-treatment)
- **`class_weight='balanced'`** to handle severe class imbalance (ESI-1 has only 1 patient)

## Top Predictive Features

1. Days since last encounter (15.5%)
2. Heart rate (9.1%)
3. Body temperature (8.6%)
4. Age (8.4%)
5. Oxygen saturation (7.7%)

## Directory Structure

```
models/
├── README.md                          # This file
├── README_V2_PIPELINE.md             # Detailed pipeline documentation
├── ALTERNATIVE_LABELING_STRATEGIES.md # Other approaches explored
├── snomed_triage_mapping.json        # 26 SNOMED codes → ESI mappings
├── data/
│   ├── preprocessor_v2.py            # Step 1: FHIR → 23 features
│   ├── label_generator_v2.py         # Step 2: SNOMED → ESI labels
│   ├── feature_engineering_v2.py     # Step 3: Encoding + splits
│   ├── extracted_features_v2.parquet
│   ├── labeled_data_v2.parquet
│   ├── X_train.parquet               # Training data (66 patients)
│   ├── X_val.parquet                 # Validation data (22 patients)
│   └── X_test.parquet                # Test data (23 patients)
└── baseline/
    ├── train_clean_models.py         # Step 4: Train 4 models
    ├── xgboost_v2.pkl                # Best model (87% accuracy)
    ├── random_forest_v2.pkl
    ├── lightgbm_v2.pkl
    ├── logistic_regression_v2.pkl
    └── model_comparison_v2.json      # Performance comparison
```

## Limitations

- **Small dataset:** 111 patients (23 in test set)
- **SNOMED coverage:** Only 26 of ~350,000 codes mapped; unknowns default to ESI-4
- **Class imbalance:** ESI-1 has 1 patient, ESI-3 has 2; SMOTE failed due to small classes

See `README_V2_PIPELINE.md` for the full detailed documentation and `ALTERNATIVE_LABELING_STRATEGIES.md` for other approaches explored.
