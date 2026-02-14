"""
Train Multiple Models on Clean Data (V2)

Trains XGBoost, Random Forest, LightGBM, and Logistic Regression on validated,
temporally-clean FHIR triage data.

CRITICAL DIFFERENCES FROM V1:
- NO temporal leakage (features available at t=0 only)
- NO circular dependencies (encounter.class removed)
- Labels from SNOMED codes, not formulas
- Using class_weight='balanced' for extreme class imbalance

Input: Processed train/val/test splits from feature_engineering_v2.py
Output: Trained models + evaluation metrics + comparison report
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import joblib


class ModelTrainer:
    """Train and evaluate multiple models on clean triage data"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.models = {}
        self.results = {}

    def load_data(self) -> Dict:
        """Load processed train/val/test splits"""
        print("="*80)
        print("LOADING PROCESSED DATA")
        print("="*80)

        data = {}

        # Load training data
        data['X_train'] = pd.read_parquet(self.data_dir / 'X_train.parquet')
        data['y_train'] = pd.read_parquet(self.data_dir / 'y_esi_train.parquet').squeeze()

        # Load validation data
        data['X_val'] = pd.read_parquet(self.data_dir / 'X_val.parquet')
        data['y_val'] = pd.read_parquet(self.data_dir / 'y_esi_val.parquet').squeeze()

        # Load test data
        data['X_test'] = pd.read_parquet(self.data_dir / 'X_test.parquet')
        data['y_test'] = pd.read_parquet(self.data_dir / 'y_esi_test.parquet').squeeze()

        print(f"\nDataset sizes:")
        print(f"  Train: {len(data['X_train'])} samples, {len(data['X_train'].columns)} features")
        print(f"  Val: {len(data['X_val'])} samples")
        print(f"  Test: {len(data['X_test'])} samples")

        print(f"\nClass distributions:")
        print(f"  Train: {data['y_train'].value_counts().sort_index().to_dict()}")
        print(f"  Val: {data['y_val'].value_counts().sort_index().to_dict()}")
        print(f"  Test: {data['y_test'].value_counts().sort_index().to_dict()}")

        return data

    def train_xgboost(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series
    ) -> XGBClassifier:
        """
        Train XGBoost classifier

        NOTE: XGBoost expects 0-indexed labels, so we remap ESI 1-5 → 0-4
        """
        print("\n" + "="*80)
        print("TRAINING XGBOOST")
        print("="*80)

        # Remap ESI labels from 1-5 to 0-4 for XGBoost
        y_train_xgb = y_train - 1
        y_val_xgb = y_val - 1

        # Calculate class weights (using remapped labels)
        class_counts = y_train_xgb.value_counts()
        total = len(y_train_xgb)
        class_weights = {cls: total / (len(class_counts) * count) for cls, count in class_counts.items()}

        print(f"\nClass weights (0-indexed): {class_weights}")

        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='mlogloss',
            early_stopping_rounds=20,
            # Use sample_weight instead for multiclass
        )

        # Calculate sample weights
        sample_weights = y_train_xgb.map(class_weights)

        # Train with early stopping
        eval_set = [(X_val, y_val_xgb)]
        model.fit(
            X_train,
            y_train_xgb,
            sample_weight=sample_weights,
            eval_set=eval_set,
            verbose=False
        )

        print(f"\nBest iteration: {model.best_iteration}")
        print(f"Best validation score: {model.best_score:.4f}")

        # Store remapping info
        model.label_offset = 1  # We'll add this back during prediction

        return model

    def train_random_forest(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> RandomForestClassifier:
        """Train Random Forest classifier"""
        print("\n" + "="*80)
        print("TRAINING RANDOM FOREST")
        print("="*80)

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',  # Handle class imbalance
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        print(f"\nFeature importances (top 10):")
        feature_importances = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        for i, row in feature_importances.head(10).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")

        return model

    def train_lightgbm(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series
    ) -> LGBMClassifier:
        """Train LightGBM classifier"""
        print("\n" + "="*80)
        print("TRAINING LIGHTGBM")
        print("="*80)

        model = LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            class_weight='balanced',
            random_state=42,
            verbose=-1
        )

        # Train with early stopping
        eval_set = [(X_val, y_val)]
        model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            callbacks=[
                #lgb.early_stopping(stopping_rounds=20),
                #lgb.log_evaluation(period=0)
            ]
        )

        print(f"\nBest iteration: {model.best_iteration_ if hasattr(model, 'best_iteration_') else 'N/A'}")

        return model

    def train_logistic_regression(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> LogisticRegression:
        """Train Logistic Regression classifier"""
        print("\n" + "="*80)
        print("TRAINING LOGISTIC REGRESSION")
        print("="*80)

        model = LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42,
            multi_class='multinomial',  # For 5-class problem
            solver='lbfgs'
        )

        model.fit(X_train, y_train)

        print(f"\nClasses: {model.classes_}")
        print(f"Coefficients shape: {model.coef_.shape}")

        return model

    def evaluate_model(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        model_name: str
    ) -> Dict:
        """
        Evaluate model on test set

        Returns comprehensive metrics including per-class and overall performance
        """
        print(f"\n" + "="*80)
        print(f"EVALUATING {model_name.upper()}")
        print("="*80)

        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        # Remap XGBoost predictions back to ESI 1-5
        if hasattr(model, 'label_offset'):
            y_pred = y_pred + model.label_offset

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)

        # Multi-class metrics (weighted averages)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        # AUROC (one-vs-rest for multiclass)
        try:
            auroc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        except:
            auroc = None

        results = {
            'model_name': model_name,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auroc': auroc,
            'predictions': y_pred.tolist(),
            'true_labels': y_test.tolist()
        }

        print(f"\n{model_name} Performance:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        if auroc:
            print(f"  AUROC: {auroc:.4f}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(cm)

        # Per-class metrics
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        print(f"\nPer-Class Metrics:")
        for esi_level in sorted(y_test.unique()):
            if str(esi_level) in report:
                metrics = report[str(esi_level)]
                print(f"  ESI-{esi_level}: Precision={metrics['precision']:.3f}, "
                      f"Recall={metrics['recall']:.3f}, F1={metrics['f1-score']:.3f}, "
                      f"Support={int(metrics['support'])}")

        results['confusion_matrix'] = cm.tolist()
        results['classification_report'] = report

        return results

    def train_all_models(self, data: Dict) -> Dict:
        """Train all models"""
        print("\n" + "="*80)
        print("TRAINING ALL MODELS")
        print("="*80)

        # 1. XGBoost
        self.models['xgboost'] = self.train_xgboost(
            data['X_train'], data['y_train'],
            data['X_val'], data['y_val']
        )

        # 2. Random Forest
        self.models['random_forest'] = self.train_random_forest(
            data['X_train'], data['y_train']
        )

        # 3. LightGBM
        self.models['lightgbm'] = self.train_lightgbm(
            data['X_train'], data['y_train'],
            data['X_val'], data['y_val']
        )

        # 4. Logistic Regression
        self.models['logistic_regression'] = self.train_logistic_regression(
            data['X_train'], data['y_train']
        )

        return self.models

    def evaluate_all_models(self, data: Dict) -> Dict:
        """Evaluate all models on test set"""
        print("\n" + "="*80)
        print("EVALUATING ALL MODELS ON TEST SET")
        print("="*80)

        for model_name, model in self.models.items():
            self.results[model_name] = self.evaluate_model(
                model,
                data['X_test'],
                data['y_test'],
                model_name
            )

        return self.results

    def save_models(self, output_dir: Path):
        """Save trained models"""
        print("\n" + "="*80)
        print("SAVING MODELS")
        print("="*80)

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        for model_name, model in self.models.items():
            model_path = output_dir / f'{model_name}_v2.pkl'
            joblib.dump(model, model_path)
            print(f"  Saved {model_name}: {model_path}")

    def save_results(self, output_dir: Path):
        """Save evaluation results"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # Save summary
        summary = {
            model_name: {
                'accuracy': results['accuracy'],
                'precision': results['precision'],
                'recall': results['recall'],
                'f1_score': results['f1_score'],
                'auroc': results['auroc']
            }
            for model_name, results in self.results.items()
        }

        summary_path = output_dir / 'model_comparison_v2.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n  Saved comparison: {summary_path}")

        # Save detailed results
        for model_name, results in self.results.items():
            results_path = output_dir / f'{model_name}_results_v2.json'
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"  Saved {model_name} results: {results_path}")

    def compare_models(self):
        """Print model comparison table"""
        print("\n" + "="*80)
        print("MODEL COMPARISON (CLEAN DATA V2)")
        print("="*80)

        comparison = pd.DataFrame({
            'Model': [],
            'Accuracy': [],
            'Precision': [],
            'Recall': [],
            'F1-Score': [],
            'AUROC': []
        })

        for model_name, results in self.results.items():
            comparison = pd.concat([comparison, pd.DataFrame({
                'Model': [model_name.replace('_', ' ').title()],
                'Accuracy': [f"{results['accuracy']:.4f}"],
                'Precision': [f"{results['precision']:.4f}"],
                'Recall': [f"{results['recall']:.4f}"],
                'F1-Score': [f"{results['f1_score']:.4f}"],
                'AUROC': [f"{results['auroc']:.4f}" if results['auroc'] else 'N/A']
            })], ignore_index=True)

        print(f"\n{comparison.to_string(index=False)}")

        # Find best model
        best_model = max(self.results.items(), key=lambda x: x[1]['f1_score'])
        print(f"\n🏆 Best Model: {best_model[0].replace('_', ' ').title()} "
              f"(F1-Score: {best_model[1]['f1_score']:.4f})")


def main():
    """Run training pipeline"""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    models_dir = script_dir

    print("="*80)
    print("MODEL TRAINING PIPELINE - CLEAN DATA V2")
    print("="*80)
    print(f"\nData directory: {data_dir}")
    print(f"Models directory: {models_dir}")

    # Initialize trainer
    trainer = ModelTrainer(data_dir)

    # Load data
    data = trainer.load_data()

    # Train models
    trainer.train_all_models(data)

    # Evaluate models
    trainer.evaluate_all_models(data)

    # Compare models
    trainer.compare_models()

    # Save models and results
    trainer.save_models(models_dir)
    trainer.save_results(models_dir)

    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
