"""
Feature Engineering Pipeline V2 - Clean Data Processing

Processes the validated triage-time features for ML training:
1. Handle missing values appropriately
2. Encode categorical features (SNOMED codes, race, gender)
3. Create train/validation/test splits with stratification
4. Address class imbalance (SMOTE for minority classes)
5. Save processed datasets for model training

Input: labeled_data_v2.parquet (validated clean data)
Output: Processed train/val/test sets ready for ML
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Feature engineering pipeline for triage data"""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.df = None
        self.scaler = StandardScaler()
        self.label_encoders = {}

        # Feature groups
        self.numeric_features = [
            'age',
            'heart_rate',
            'respiratory_rate',
            'blood_pressure_systolic',
            'blood_pressure_diastolic',
            'oxygen_saturation',
            'body_temperature',
            'num_prior_encounters_total',
            'num_prior_encounters_emergency',
            'num_prior_encounters_inpatient',
            'num_prior_encounters_ambulatory',
            'days_since_last_encounter',
            'hour_of_day',
            'day_of_week',
            'is_weekend'
        ]

        self.categorical_features = [
            'gender',
            'race',
            'reason_code_snomed'
        ]

        # Features to exclude from model input
        self.exclude_features = [
            'patient_id',
            'file_path',
            'gender_male',
            'gender_female',
            'reason_code_display',
            'esi_level',
            'esi_label',
            'risk_level',
            'risk_label'
        ]

    def load_data(self) -> pd.DataFrame:
        """Load labeled data"""
        print(f"Loading data from: {self.data_path}")
        self.df = pd.read_parquet(self.data_path)
        print(f"Loaded {len(self.df)} patients with {len(self.df.columns)} columns")
        return self.df

    def analyze_missing_values(self) -> pd.DataFrame:
        """Analyze missing values in features"""
        print("\n" + "="*80)
        print("MISSING VALUE ANALYSIS")
        print("="*80)

        missing_stats = []
        for col in self.numeric_features + self.categorical_features:
            if col in self.df.columns:
                missing_count = self.df[col].isna().sum()
                missing_pct = (missing_count / len(self.df)) * 100
                missing_stats.append({
                    'feature': col,
                    'missing_count': missing_count,
                    'missing_pct': missing_pct,
                    'dtype': str(self.df[col].dtype)
                })

        missing_df = pd.DataFrame(missing_stats).sort_values('missing_pct', ascending=False)

        print(f"\nFeatures with missing values:")
        for _, row in missing_df[missing_df['missing_pct'] > 0].iterrows():
            print(f"  {row['feature']}: {row['missing_count']}/{len(self.df)} ({row['missing_pct']:.1f}%)")

        return missing_df

    def handle_missing_values(self) -> pd.DataFrame:
        """
        Handle missing values with appropriate strategies

        Strategy:
        - Vital signs: Forward fill from patient history, then median imputation
        - Demographics: Mode imputation (should be complete)
        - Patient history: Fill with 0 (no prior encounters)
        - Temporal: Should be complete (drop if missing)
        """
        print("\n" + "="*80)
        print("HANDLING MISSING VALUES")
        print("="*80)

        df = self.df.copy()

        # 1. Vital signs - median imputation
        vital_features = [
            'heart_rate', 'respiratory_rate', 'blood_pressure_systolic',
            'blood_pressure_diastolic', 'oxygen_saturation', 'body_temperature'
        ]

        # Default values for vitals if ALL values are missing
        vital_defaults = {
            'heart_rate': 75.0,
            'respiratory_rate': 16.0,
            'blood_pressure_systolic': 120.0,
            'blood_pressure_diastolic': 80.0,
            'oxygen_saturation': 97.0,
            'body_temperature': 37.0
        }

        for feature in vital_features:
            if feature in df.columns:
                missing_before = df[feature].isna().sum()
                median_value = df[feature].median()

                # If median is NaN (all values missing), use default
                if pd.isna(median_value):
                    median_value = vital_defaults.get(feature, 0.0)
                    print(f"  {feature}: All values missing, using default {median_value:.2f}")

                df[feature] = df[feature].fillna(median_value)

                if missing_before > 0 and not pd.isna(df[feature].median()):
                    print(f"  {feature}: Filled {missing_before} missing values with median {median_value:.2f}")

        # 2. Demographics - mode imputation
        if 'race' in df.columns:
            missing_before = df['race'].isna().sum()
            mode_value = df['race'].mode()[0] if len(df['race'].mode()) > 0 else 'unknown'
            df['race'] = df['race'].fillna(mode_value)
            print(f"  race: Filled {missing_before} missing values with mode '{mode_value}'")

        # 3. Patient history - fill with 0
        history_features = [
            'num_prior_encounters_total', 'num_prior_encounters_emergency',
            'num_prior_encounters_inpatient', 'num_prior_encounters_ambulatory',
            'days_since_last_encounter'
        ]

        for feature in history_features:
            if feature in df.columns:
                missing_before = df[feature].isna().sum()
                df[feature] = df[feature].fillna(0)
                if missing_before > 0:
                    print(f"  {feature}: Filled {missing_before} missing values with 0")

        # 4. SNOMED codes - fill with 'unknown'
        if 'reason_code_snomed' in df.columns:
            missing_before = df['reason_code_snomed'].isna().sum()
            df['reason_code_snomed'] = df['reason_code_snomed'].fillna('unknown')
            if missing_before > 0:
                print(f"  reason_code_snomed: Filled {missing_before} missing values with 'unknown'")

        self.df = df
        return df

    def encode_categorical_features(self) -> pd.DataFrame:
        """
        Encode categorical features

        Strategy:
        - SNOMED codes: One-hot encoding (many unique values but sparse)
        - Gender: Already has gender_male/gender_female, use those
        - Race: One-hot encoding
        """
        print("\n" + "="*80)
        print("ENCODING CATEGORICAL FEATURES")
        print("="*80)

        df = self.df.copy()

        # 1. SNOMED codes - one-hot encode
        if 'reason_code_snomed' in df.columns:
            print(f"\nEncoding SNOMED codes...")
            unique_codes = df['reason_code_snomed'].nunique()
            print(f"  Unique SNOMED codes: {unique_codes}")

            # One-hot encode
            snomed_dummies = pd.get_dummies(df['reason_code_snomed'], prefix='snomed')
            df = pd.concat([df, snomed_dummies], axis=1)
            print(f"  Created {len(snomed_dummies.columns)} SNOMED indicator columns")

        # 2. Race - one-hot encode
        if 'race' in df.columns:
            print(f"\nEncoding race...")
            unique_races = df['race'].nunique()
            print(f"  Unique races: {unique_races}")

            race_dummies = pd.get_dummies(df['race'], prefix='race')
            df = pd.concat([df, race_dummies], axis=1)
            print(f"  Created {len(race_dummies.columns)} race indicator columns")

        # 3. Gender - already encoded as gender_male/gender_female, keep those
        print(f"\nGender encoding:")
        print(f"  Using existing gender_male/gender_female columns")

        self.df = df
        return df

    def prepare_features_and_labels(self) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepare feature matrix X and label vectors y

        Returns:
            X: Feature matrix
            y_esi: ESI labels (1-5)
            y_risk: Risk labels (0=Low, 1=Medium, 2=High)
        """
        print("\n" + "="*80)
        print("PREPARING FEATURES AND LABELS")
        print("="*80)

        df = self.df.copy()

        # Get all columns that should be features
        feature_cols = []
        for col in df.columns:
            if col not in self.exclude_features and col not in self.categorical_features:
                # Include numeric features and one-hot encoded categorical features
                feature_cols.append(col)

        X = df[feature_cols]
        y_esi = df['esi_level']
        y_risk = df['risk_level']

        print(f"\nFeature matrix shape: {X.shape}")
        print(f"  Total features: {len(feature_cols)}")
        print(f"  Numeric features: {len([c for c in feature_cols if c in self.numeric_features])}")
        print(f"  One-hot encoded features: {len([c for c in feature_cols if c.startswith('snomed_') or c.startswith('race_')])}")
        print(f"  Binary features: {len([c for c in feature_cols if c in ['gender_male', 'gender_female', 'is_weekend']])}")

        print(f"\nLabel distributions:")
        print(f"  ESI levels: {y_esi.value_counts().sort_index().to_dict()}")
        print(f"  Risk levels: {y_risk.value_counts().sort_index().to_dict()}")

        return X, y_esi, y_risk

    def create_train_val_test_split(
        self,
        X: pd.DataFrame,
        y_esi: pd.Series,
        y_risk: pd.Series,
        test_size: float = 0.2,
        val_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        Create stratified train/validation/test splits

        Strategy:
        - Stratify on risk_level instead of ESI (ESI has classes with only 1 sample)
        - Group ESI 1-2 → High, ESI 3 → Medium, ESI 4-5 → Low
        - 60% train, 20% validation, 20% test
        """
        print("\n" + "="*80)
        print("CREATING TRAIN/VALIDATION/TEST SPLITS")
        print("="*80)

        print(f"\nNote: Stratifying on risk_level (not ESI) due to extremely small ESI-1 class (n=1)")

        # First split: train+val vs test (stratify on risk_level)
        X_trainval, X_test, y_esi_trainval, y_esi_test, y_risk_trainval, y_risk_test = train_test_split(
            X, y_esi, y_risk,
            test_size=test_size,
            stratify=y_risk,  # Use risk_level for stratification
            random_state=random_state
        )

        # Second split: train vs val
        val_size_adjusted = val_size / (1 - test_size)  # Adjust for remaining data
        X_train, X_val, y_esi_train, y_esi_val, y_risk_train, y_risk_val = train_test_split(
            X_trainval, y_esi_trainval, y_risk_trainval,
            test_size=val_size_adjusted,
            stratify=y_risk_trainval,  # Use risk_level for stratification
            random_state=random_state
        )

        splits = {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_esi_train': y_esi_train,
            'y_esi_val': y_esi_val,
            'y_esi_test': y_esi_test,
            'y_risk_train': y_risk_train,
            'y_risk_val': y_risk_val,
            'y_risk_test': y_risk_test
        }

        print(f"\nSplit sizes:")
        print(f"  Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
        print(f"  Validation: {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
        print(f"  Test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")

        print(f"\nESI distribution in splits:")
        print(f"  Train: {y_esi_train.value_counts().sort_index().to_dict()}")
        print(f"  Val: {y_esi_val.value_counts().sort_index().to_dict()}")
        print(f"  Test: {y_esi_test.value_counts().sort_index().to_dict()}")

        return splits

    def apply_smote(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        sampling_strategy: str = 'auto',
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Apply SMOTE to balance training data

        WARNING: Only apply to training data, not validation/test!
        """
        print("\n" + "="*80)
        print("APPLYING SMOTE FOR CLASS BALANCING")
        print("="*80)

        print(f"\nBefore SMOTE:")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Class distribution: {y_train.value_counts().sort_index().to_dict()}")

        # SMOTE requires at least 2 samples per class
        # Check if all classes have enough samples
        class_counts = y_train.value_counts()
        min_samples = class_counts.min()

        if min_samples < 2:
            print(f"\n⚠️  WARNING: Some classes have < 2 samples. SMOTE requires at least 2.")
            print(f"  Skipping SMOTE. Consider using class_weight='balanced' in model instead.")
            return X_train, y_train

        # Apply SMOTE
        smote = SMOTE(sampling_strategy=sampling_strategy, random_state=random_state, k_neighbors=1)

        try:
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

            print(f"\nAfter SMOTE:")
            print(f"  Training samples: {len(X_resampled)}")
            print(f"  Class distribution: {pd.Series(y_resampled).value_counts().sort_index().to_dict()}")

            # Convert back to DataFrame/Series with original column names
            X_resampled = pd.DataFrame(X_resampled, columns=X_train.columns)
            y_resampled = pd.Series(y_resampled, name=y_train.name)

            return X_resampled, y_resampled

        except Exception as e:
            print(f"\n⚠️  SMOTE failed: {e}")
            print(f"  Continuing without SMOTE. Use class_weight='balanced' in models.")
            return X_train, y_train

    def save_processed_data(self, splits: Dict, output_dir: Path, apply_smote_flag: bool = False):
        """Save processed datasets"""
        print("\n" + "="*80)
        print("SAVING PROCESSED DATA")
        print("="*80)

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # Save splits
        for split_name, split_data in splits.items():
            output_path = output_dir / f'{split_name}.parquet'

            # Convert Series to DataFrame for parquet
            if isinstance(split_data, pd.Series):
                split_data = split_data.to_frame()

            split_data.to_parquet(output_path, index=False)
            print(f"  Saved {split_name}: {output_path}")

        # Save SMOTE-balanced training data if requested
        if apply_smote_flag:
            X_train_smote, y_esi_train_smote = self.apply_smote(
                splits['X_train'],
                splits['y_esi_train']
            )

            X_train_smote.to_parquet(output_dir / 'X_train_smote.parquet', index=False)
            y_esi_train_smote.to_frame().to_parquet(output_dir / 'y_esi_train_smote.parquet', index=False)
            print(f"  Saved X_train_smote: {output_dir / 'X_train_smote.parquet'}")
            print(f"  Saved y_esi_train_smote: {output_dir / 'y_esi_train_smote.parquet'}")

        print(f"\n✓ All processed data saved to: {output_dir}")


def main():
    """Run feature engineering pipeline"""
    script_dir = Path(__file__).parent
    data_path = script_dir / 'labeled_data_v2.parquet'
    output_dir = script_dir

    print("="*80)
    print("FEATURE ENGINEERING PIPELINE V2")
    print("="*80)

    # Initialize
    engineer = FeatureEngineer(data_path)

    # Load data
    engineer.load_data()

    # Analyze missing values
    engineer.analyze_missing_values()

    # Handle missing values
    engineer.handle_missing_values()

    # Encode categorical features
    engineer.encode_categorical_features()

    # Prepare features and labels
    X, y_esi, y_risk = engineer.prepare_features_and_labels()

    # Create splits
    splits = engineer.create_train_val_test_split(X, y_esi, y_risk)

    # Save processed data
    engineer.save_processed_data(splits, output_dir, apply_smote_flag=True)

    print("\n" + "="*80)
    print("FEATURE ENGINEERING COMPLETE")
    print("="*80)
    print(f"\nReady for model training!")
    print(f"  Use X_train.parquet and y_esi_train.parquet for training")
    print(f"  Use X_train_smote.parquet and y_esi_train_smote.parquet for balanced training")
    print(f"  Use X_val.parquet and y_esi_val.parquet for validation")
    print(f"  Use X_test.parquet and y_esi_test.parquet for final evaluation")


if __name__ == '__main__':
    main()
