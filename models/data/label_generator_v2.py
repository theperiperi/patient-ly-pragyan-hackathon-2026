"""
Label Generator V2 - SNOMED-Based ESI Triage Labels

CRITICAL FIXES FROM VALIDATION:
1. NO encounter.class in labeling (that's the outcome, not the input!)
2. Labels derived ONLY from chief complaint (Encounter.reasonCode SNOMED codes)
3. NO circular dependencies - features and labels are independent

This generates ESI (Emergency Severity Index) levels 1-5 from SNOMED-CT codes.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple


class SNOMEDBasedLabelGenerator:
    """Generate ESI triage labels from SNOMED chief complaint codes ONLY"""

    def __init__(self, snomed_mapping_path: str = None):
        """
        Args:
            snomed_mapping_path: Path to snomed_triage_mapping.json
        """
        if snomed_mapping_path is None:
            script_dir = Path(__file__).parent
            snomed_mapping_path = script_dir.parent / 'snomed_triage_mapping.json'

        with open(snomed_mapping_path, 'r') as f:
            self.snomed_mapping = json.load(f)

        # Build fast lookup dict from the snomed_mappings structure
        self.code_to_esi = {}

        # Iterate through all categories in snomed_mappings
        for category_name, mappings_list in self.snomed_mapping.get('snomed_mappings', {}).items():
            for mapping in mappings_list:
                code = mapping.get('code')
                esi = mapping.get('esi_level', 4)  # Default to ESI 4 if not specified
                if code:
                    self.code_to_esi[code] = esi

        print(f"✓ Loaded {len(self.code_to_esi)} SNOMED → ESI mappings")

    def generate_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate ESI labels from patient data

        IMPORTANT: This uses ONLY the following fields:
        - Encounter reasonCode (chief complaint)
        - Initial vital signs (for refinement)

        It does NOT use:
        - encounter.class (that's the outcome!)
        - lab values (not available at triage)
        - final diagnoses (assigned after evaluation)

        Args:
            df: DataFrame with extracted features including 'reason_code_snomed'

        Returns:
            DataFrame with added esi_level, esi_label, risk_level columns
        """
        df = df.copy()

        print("\nGenerating ESI labels from SNOMED chief complaints...")

        # Get ESI level from SNOMED code
        df['esi_level'] = df.apply(self._get_esi_from_snomed, axis=1)

        # Refine with vital signs (if available)
        df['esi_level'] = df.apply(self._refine_with_vitals, axis=1)

        # Create categorical label
        df['esi_label'] = df['esi_level'].map({
            1: 'ESI-1 (Immediate)',
            2: 'ESI-2 (Emergent)',
            3: 'ESI-3 (Urgent)',
            4: 'ESI-4 (Less Urgent)',
            5: 'ESI-5 (Non-Urgent)',
        })

        # Map to 3-class risk level for backwards compatibility
        df['risk_level'] = df['esi_level'].apply(self._esi_to_risk_level)
        df['risk_label'] = df['risk_level'].map({
            0: 'Low',
            1: 'Medium',
            2: 'High'
        })

        # Distribution
        print("\nESI Level Distribution:")
        print(df['esi_label'].value_counts().sort_index())

        print("\nRisk Level Distribution (3-class):")
        print(df['risk_level'].value_counts().sort_index())

        return df

    def _get_esi_from_snomed(self, row: pd.Series) -> int:
        """
        Get ESI level from SNOMED chief complaint code

        Returns ESI 1-5 based purely on chief complaint
        """
        # Get SNOMED code from reason_code column
        snomed_code = row.get('reason_code_snomed', '')

        # Handle missing/unknown codes
        if pd.isna(snomed_code) or snomed_code == '' or snomed_code == 'unknown':
            # Default to ESI 4 (less urgent) for unknown complaints
            return 4

        # Lookup in mapping
        esi = self.code_to_esi.get(str(snomed_code), 4)

        return esi

    def _refine_with_vitals(self, row: pd.Series) -> int:
        """
        Refine ESI level based on vital signs at arrival

        Critical vitals override chief complaint and force ESI 1-2
        This is clinically appropriate - unstable vitals = higher acuity
        """
        base_esi = row['esi_level']

        # Critical vital signs that override ESI level
        critical_vitals = False

        # Oxygen saturation < 88% (severe hypoxemia)
        spo2 = row.get('oxygen_saturation')
        if pd.notna(spo2) and spo2 < 88:
            critical_vitals = True

        # Systolic BP < 90 (hypotension)
        sbp = row.get('blood_pressure_systolic')
        if pd.notna(sbp) and sbp < 90:
            critical_vitals = True

        # Heart rate < 40 or > 130 (severe brady/tachycardia)
        hr = row.get('heart_rate')
        if pd.notna(hr) and (hr < 40 or hr > 130):
            critical_vitals = True

        # Respiratory rate < 8 or > 30 (severe resp distress)
        rr = row.get('respiratory_rate')
        if pd.notna(rr) and (rr < 8 or rr > 30):
            critical_vitals = True

        # If critical vitals, force to ESI 1 or 2
        if critical_vitals:
            return min(base_esi, 2)

        # Abnormal vitals (not critical) - upgrade by 1 level
        abnormal_vitals = False

        if pd.notna(spo2) and spo2 < 92:
            abnormal_vitals = True

        if pd.notna(hr) and (hr < 50 or hr > 110):
            abnormal_vitals = True

        if pd.notna(rr) and (rr < 10 or rr > 24):
            abnormal_vitals = True

        if abnormal_vitals and base_esi > 1:
            return base_esi - 1  # Upgrade (lower ESI number = higher acuity)

        return base_esi

    def _esi_to_risk_level(self, esi: int) -> int:
        """
        Map ESI 1-5 to 3-class risk level for backwards compatibility

        ESI 1-2 → High risk (2)
        ESI 3   → Medium risk (1)
        ESI 4-5 → Low risk (0)
        """
        if esi <= 2:
            return 2  # High
        elif esi == 3:
            return 1  # Medium
        else:
            return 0  # Low

    def get_label_statistics(self, df: pd.DataFrame) -> Dict:
        """Get statistics about generated labels"""
        stats = {
            'total_patients': len(df),
            'esi_distribution': df['esi_level'].value_counts().to_dict(),
            'risk_distribution': df['risk_level'].value_counts().to_dict(),
            'missing_snomed_count': df['reason_code_snomed'].isna().sum(),
        }
        return stats


def main():
    """Test label generation with SNOMED-only approach"""
    from pathlib import Path

    # This requires preprocessed data with reason_code_snomed field
    script_dir = Path(__file__).parent

    # We'll need to re-extract features to get reason_code_snomed
    print("="*80)
    print("SNOMED-BASED LABEL GENERATION")
    print("="*80)

    print("\nNOTE: This requires preprocessor to extract reason_code_snomed from FHIR")
    print("Run preprocessor_v2.py first to get clean features with SNOMED codes")

    # Check if we have the data
    features_path = script_dir / 'extracted_features_v2.parquet'

    if not features_path.exists():
        print(f"\n⚠️  Missing: {features_path}")
        print("Run preprocessor_v2.py first!")
        return

    # Load features
    df = pd.read_parquet(features_path)
    print(f"\nLoaded {len(df)} patients")

    # Generate labels
    generator = SNOMEDBasedLabelGenerator()
    df_labeled = generator.generate_labels(df)

    # Statistics
    print("\n" + "="*80)
    print("LABEL STATISTICS")
    print("="*80)

    stats = generator.get_label_statistics(df_labeled)

    print(f"\nTotal patients: {stats['total_patients']}")
    print(f"Missing SNOMED codes: {stats['missing_snomed_count']}")

    # Save
    output_path = script_dir / 'labeled_data_v2.parquet'
    df_labeled.to_parquet(output_path, index=False)
    print(f"\n✓ Saved labeled data to {output_path}")

    # Examples
    print("\n" + "="*80)
    print("EXAMPLE LABELS")
    print("="*80)

    for esi in [1, 2, 3, 4, 5]:
        examples = df_labeled[df_labeled['esi_level'] == esi].head(1)
        if len(examples) > 0:
            ex = examples.iloc[0]
            print(f"\n{ex['esi_label']}:")
            print(f"  SNOMED: {ex.get('reason_code_snomed', 'N/A')}")
            print(f"  Age: {ex.get('age', 'N/A')}")
            print(f"  SpO2: {ex.get('oxygen_saturation', 'N/A')}")
            print(f"  HR: {ex.get('heart_rate', 'N/A')}")


if __name__ == '__main__':
    main()
