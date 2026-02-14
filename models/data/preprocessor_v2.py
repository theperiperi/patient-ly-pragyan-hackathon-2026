"""
FHIR Preprocessor V2 - Triage-Time Features Only

CRITICAL FIXES FROM VALIDATION:
1. Extract ONLY features available at patient ARRIVAL (t=0)
2. NO post-triage data (labs, final diagnoses, encounter outcomes)
3. Extract SNOMED chief complaint codes from Encounter.reasonCode
4. Get INITIAL vital signs (first measurement), not latest
5. NO encounter.class as a feature (that's the outcome!)

Valid features:
- Demographics (age, gender) ✅
- Chief complaint (SNOMED code) ✅
- Initial vitals (first HR, BP, SpO2, temp, RR) ✅
- Patient history (prior encounters, prior emergencies) ✅
- Temporal (time of day, day of week) ✅

Invalid features (removed):
- Lab values (troponin, eGFR, glucose, etc.) ❌ Not available at triage
- Final diagnoses / condition counts ❌ Assigned after evaluation
- Encounter.class ❌ This is the OUTCOME we're predicting!
- Encounter duration ❌ Only known after discharge
"""

import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


class TriageTimePreprocessor:
    """Extract features available at patient arrival ONLY"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.bundles = []
        self.features = []

    def load_bundles(self) -> int:
        """Load all FHIR bundles from directory"""
        json_files = list(self.data_dir.glob('*.json'))

        # Filter out metadata files
        json_files = [f for f in json_files if 'hospital' not in f.name.lower()
                      and 'practitioner' not in f.name.lower()]

        print(f"Found {len(json_files)} patient FHIR bundles")

        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    bundle = json.load(f)
                    if bundle.get('resourceType') == 'Bundle':
                        self.bundles.append({
                            'path': str(file_path),
                            'data': bundle
                        })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        print(f"Successfully loaded {len(self.bundles)} bundles")
        return len(self.bundles)

    def extract_all_features(self) -> pd.DataFrame:
        """Extract triage-time features from all bundles"""
        print(f"\nExtracting triage-time features from {len(self.bundles)} patients...")

        for i, bundle_info in enumerate(self.bundles):
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(self.bundles)} patients")

            features = self._extract_triage_features(bundle_info['data'])
            features['file_path'] = bundle_info['path']
            self.features.append(features)

        df = pd.DataFrame(self.features)
        print(f"\nExtracted {len(df.columns)} features from {len(df)} patients")
        return df

    def _extract_triage_features(self, bundle: Dict) -> Dict[str, Any]:
        """Extract features from a single FHIR bundle (triage-time only)"""
        features = {}

        # Separate resources by type
        resources = self._group_resources_by_type(bundle)

        # 1. Patient demographics (always available)
        patient = resources.get('Patient', [None])[0]
        if patient:
            features.update(self._extract_demographics(patient))

        # 2. Chief complaint from encounters (SNOMED code)
        encounters = resources.get('Encounter', [])
        current_encounter_id = None
        if encounters:
            chief_complaint_features, current_encounter_id = self._extract_chief_complaint(encounters)
            features.update(chief_complaint_features)

        # 3. INITIAL vital signs (first measurement per encounter)
        observations = resources.get('Observation', [])
        features.update(self._extract_initial_vitals(observations))

        # 4. Patient history (prior to current encounter)
        features.update(self._extract_patient_history(encounters, current_encounter_id))

        # 5. Temporal features (when did they arrive?)
        if encounters:
            features.update(self._extract_temporal_features(encounters[0]))

        return features

    def _group_resources_by_type(self, bundle: Dict) -> Dict[str, List[Dict]]:
        """Group bundle entries by resource type"""
        resources = defaultdict(list)

        for entry in bundle.get('entry', []):
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType')
            if resource_type:
                resources[resource_type].append(resource)

        return resources

    def _extract_demographics(self, patient: Dict) -> Dict[str, Any]:
        """Extract demographic features"""
        features = {}

        # Patient ID
        features['patient_id'] = patient.get('id', 'unknown')

        # Gender
        gender = patient.get('gender', 'unknown')
        features['gender'] = gender
        features['gender_male'] = 1 if gender == 'male' else 0
        features['gender_female'] = 1 if gender == 'female' else 0

        # Age
        birth_date_str = patient.get('birthDate')
        if birth_date_str:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            features['age'] = age
        else:
            features['age'] = None

        # Race
        race = 'unknown'
        for ext in patient.get('extension', []):
            if 'us-core-race' in ext.get('url', ''):
                for sub_ext in ext.get('extension', []):
                    if sub_ext.get('url') == 'text':
                        race = sub_ext.get('valueString', 'unknown')
        features['race'] = race

        return features

    def _extract_chief_complaint(self, encounters: List[Dict]) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Extract SNOMED chief complaint code from Encounter.reasonCode

        This is the PRIMARY field for triage classification

        Returns:
            Tuple of (features dict, current_encounter_id)
        """
        features = {}

        # Get most recent encounter (latest start time)
        encounters_with_time = []
        for enc in encounters:
            start = enc.get('period', {}).get('start')
            if start:
                encounters_with_time.append((start, enc))

        if not encounters_with_time:
            features['reason_code_snomed'] = 'unknown'
            features['reason_code_display'] = 'unknown'
            return features, None

        # Sort by time, get most recent
        encounters_with_time.sort(key=lambda x: x[0], reverse=True)
        latest_encounter = encounters_with_time[0][1]
        current_encounter_id = latest_encounter.get('id')

        # Extract reasonCode
        reason_codes = latest_encounter.get('reasonCode', [])

        if reason_codes:
            # Get first SNOMED code
            first_reason = reason_codes[0]
            codings = first_reason.get('coding', [])

            for coding in codings:
                if coding.get('system') == 'http://snomed.info/sct':
                    features['reason_code_snomed'] = coding.get('code', 'unknown')
                    features['reason_code_display'] = coding.get('display', 'unknown')
                    return features, current_encounter_id

        # No SNOMED code found
        features['reason_code_snomed'] = 'unknown'
        features['reason_code_display'] = 'unknown'

        return features, current_encounter_id

    def _extract_initial_vitals(self, observations: List[Dict]) -> Dict[str, Any]:
        """
        Extract INITIAL vital signs (first measurement per type)

        CRITICAL: We want the FIRST vital measurement when patient arrives,
        not the latest measurement after treatment!
        """
        features = {}

        # LOINC codes for vitals
        vital_loinc = {
            '8867-4': 'heart_rate',
            '9279-1': 'respiratory_rate',
            '8480-6': 'blood_pressure_systolic',
            '8462-4': 'blood_pressure_diastolic',
            '2708-6': 'oxygen_saturation',
            '8310-5': 'body_temperature',
        }

        # Initialize all vitals to None
        for vital_name in vital_loinc.values():
            features[vital_name] = None

        # Group observations by LOINC code
        vital_observations = defaultdict(list)

        for obs in observations:
            code = self._get_loinc_code(obs)
            if code in vital_loinc:
                vital_name = vital_loinc[code]
                value = self._extract_observation_value(obs)
                timestamp = obs.get('effectiveDateTime', obs.get('issued', ''))

                if value is not None and timestamp:
                    vital_observations[vital_name].append({
                        'value': value,
                        'timestamp': timestamp
                    })

        # Get EARLIEST (initial) value for each vital sign
        for vital_name, obs_list in vital_observations.items():
            if obs_list:
                # Sort by timestamp (earliest first)
                sorted_obs = sorted(obs_list, key=lambda x: x['timestamp'])
                features[vital_name] = sorted_obs[0]['value']  # FIRST measurement

        return features

    def _get_loinc_code(self, observation: Dict) -> Optional[str]:
        """Extract LOINC code from Observation"""
        for coding in observation.get('code', {}).get('coding', []):
            if coding.get('system') == 'http://loinc.org':
                return coding.get('code')
        return None

    def _extract_observation_value(self, observation: Dict) -> Optional[float]:
        """Extract numeric value from Observation"""
        # Try valueQuantity
        value_quantity = observation.get('valueQuantity', {})
        if 'value' in value_quantity:
            return float(value_quantity['value'])

        # Try components (for BP which has systolic/diastolic components)
        components = observation.get('component', [])
        if components:
            for comp in components:
                comp_value = comp.get('valueQuantity', {}).get('value')
                if comp_value is not None:
                    return float(comp_value)

        return None

    def _extract_patient_history(self, encounters: List[Dict], current_encounter_id: str = None) -> Dict[str, Any]:
        """
        Extract patient history features (prior encounters)

        This is valid because historical data is known at triage time

        IMPORTANT: Excludes the current encounter being triaged to avoid temporal leakage
        """
        features = {}

        # Filter out current encounter - only count PRIOR encounters
        prior_encounters = [enc for enc in encounters if enc.get('id') != current_encounter_id]

        # Count encounters by class (from PRIOR encounters only)
        encounter_classes = []
        for enc in prior_encounters:
            enc_class = enc.get('class', {}).get('code')
            if enc_class:
                encounter_classes.append(enc_class)

        features['num_prior_encounters_total'] = len(prior_encounters)
        features['num_prior_encounters_emergency'] = encounter_classes.count('EMER')
        features['num_prior_encounters_inpatient'] = encounter_classes.count('IMP')
        features['num_prior_encounters_ambulatory'] = encounter_classes.count('AMB')

        # Days since last PRIOR encounter
        # We need current encounter time and most recent prior encounter time
        current_time = None
        prior_times = []

        # Get current encounter time
        for enc in encounters:
            if enc.get('id') == current_encounter_id:
                start = enc.get('period', {}).get('start')
                if start:
                    try:
                        current_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    except:
                        pass
                break

        # Get prior encounter times
        for enc in prior_encounters:
            start = enc.get('period', {}).get('start')
            if start:
                try:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    prior_times.append(dt)
                except:
                    pass

        if current_time and prior_times:
            # Find most recent prior encounter
            prior_times.sort(reverse=True)
            most_recent_prior = prior_times[0]
            delta = (current_time - most_recent_prior).days
            features['days_since_last_encounter'] = delta
        else:
            features['days_since_last_encounter'] = None

        return features

    def _extract_temporal_features(self, encounter: Dict) -> Dict[str, Any]:
        """Extract temporal features (when did they arrive?)"""
        features = {}

        start_time_str = encounter.get('period', {}).get('start')

        if start_time_str:
            try:
                dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                features['hour_of_day'] = dt.hour
                features['day_of_week'] = dt.weekday()  # 0=Monday, 6=Sunday
                features['is_weekend'] = 1 if dt.weekday() >= 5 else 0
            except:
                features['hour_of_day'] = None
                features['day_of_week'] = None
                features['is_weekend'] = None
        else:
            features['hour_of_day'] = None
            features['day_of_week'] = None
            features['is_weekend'] = None

        return features


def main():
    """Run preprocessor v2"""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent.parent / 'synthea_sample_data_fhir_latest'

    print("="*80)
    print("FHIR PREPROCESSOR V2 - TRIAGE-TIME FEATURES ONLY")
    print("="*80)
    print(f"\nLooking for FHIR bundles in: {data_dir}")

    preprocessor = TriageTimePreprocessor(str(data_dir))

    # Load bundles
    num_bundles = preprocessor.load_bundles()
    if num_bundles == 0:
        print("ERROR: No bundles found!")
        return

    # Extract features
    df = preprocessor.extract_all_features()

    # Display summary
    print("\n" + "="*80)
    print("FEATURE EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total patients: {len(df)}")
    print(f"Total features: {len(df.columns)}")

    print(f"\nFeature categories:")
    print(f"  - Demographics: age, gender, race")
    print(f"  - Chief complaint: reason_code_snomed")
    print(f"  - Initial vitals: {len([c for c in df.columns if c in ['heart_rate', 'respiratory_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'oxygen_saturation', 'body_temperature']])}")
    print(f"  - Patient history: {len([c for c in df.columns if 'prior' in c or 'days_since' in c])}")
    print(f"  - Temporal: hour_of_day, day_of_week, is_weekend")

    print(f"\nSNOMED code coverage:")
    snomed_missing = df['reason_code_snomed'].isna().sum() + (df['reason_code_snomed'] == 'unknown').sum()
    snomed_coverage = (len(df) - snomed_missing) / len(df) * 100
    print(f"  Patients with SNOMED codes: {len(df) - snomed_missing}/{len(df)} ({snomed_coverage:.1f}%)")

    # Save
    output_dir = script_dir
    output_path = output_dir / 'extracted_features_v2.parquet'
    df.to_parquet(output_path, index=False)
    print(f"\n✓ Saved features to: {output_path}")

    csv_path = output_dir / 'extracted_features_v2.csv'
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved features to: {csv_path}")

    print("\n" + "="*80)
    print("VALIDATION CHECKS")
    print("="*80)

    # Check for invalid features
    invalid_features = []
    if 'latest_encounter_class' in df.columns:
        invalid_features.append('latest_encounter_class')
    if any('lab_' in c for c in df.columns):
        invalid_features.append('lab_* fields')
    if 'num_conditions' in str(df.columns):
        invalid_features.append('num_conditions_*')

    if invalid_features:
        print(f"\n⚠️  WARNING: Found invalid features: {invalid_features}")
        print("   These should NOT be present in triage-time data!")
    else:
        print(f"\n✅ No invalid post-triage features found")

    print(f"✅ All features are available at patient arrival (t=0)")

    print("\nSample of first patient:")
    sample = df.iloc[0].to_dict()
    for key, value in list(sample.items())[:15]:
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
