# Alternative Triage Labeling Strategies

## Current Approach (SNOMED-based)
**What we're doing:** Using `Encounter.reasonCode` (SNOMED chief complaint) → ESI mapping
**Coverage:** 26 manually mapped codes
**Limitation:** Only 0.007% of total SNOMED codes

---

## Alternative Approaches to Explore

### **Option 1: Multi-Signal Composite Approach** ⭐ RECOMMENDED

Instead of relying only on SNOMED, **combine multiple signals** already in the FHIR data:

#### Signals Available:
1. **Vital Signs** (already extracted)
   - Abnormal vitals = higher acuity
   - SpO2 < 88%, HR < 40 or > 130, SBP < 90, RR < 8 or > 30

2. **Medications Administered** (NEW!)
   - Nitroglycerin → Cardiac emergency (ESI 1-2)
   - Albuterol nebulizer → Respiratory distress (ESI 2-3)
   - Hydrocodone/Tramadol → Severe pain (ESI 3)
   - IV antibiotics → Infection (ESI 2-3)
   - Tylenol only → Low acuity (ESI 4-5)

3. **Procedures Performed** (NEW!)
   - Intubation → Critical (ESI 1)
   - IV placement → Moderate-high (ESI 2-3)
   - Suturing → Moderate (ESI 3)
   - Dental cleaning → Low (ESI 5)

4. **Encounter Type** (SNOMED Procedure Codes)
   - "Emergency room admission" → Higher baseline
   - "Follow-up encounter" → Lower baseline
   - "General examination" → Lowest baseline

5. **Patient History**
   - Recent ER visits → May indicate chronic high-acuity
   - Multiple prior emergencies → Higher risk

#### Proposed Algorithm:
```python
def generate_esi_label_multisignal(patient_data):
    base_score = 0

    # Signal 1: Encounter type
    if encounter_type == "Emergency room admission":
        base_score = 3  # Start at ESI 3
    elif encounter_type == "Follow-up":
        base_score = 5  # Start at ESI 5
    else:
        base_score = 4  # Default ESI 4

    # Signal 2: Critical vitals (upgrade)
    if spo2 < 88 or hr < 40 or hr > 130 or sbp < 90:
        base_score = min(base_score, 2)  # Force to ESI 1-2

    # Signal 3: Critical medications (upgrade)
    if "nitroglycerin" in medications:
        base_score = min(base_score, 1)  # Cardiac emergency
    elif "albuterol" in medications and spo2 < 92:
        base_score = min(base_score, 2)  # Respiratory emergency

    # Signal 4: High-risk procedures (upgrade)
    if "intubation" in procedures:
        base_score = 1  # Life support
    elif "IV placement" in procedures:
        base_score = min(base_score, 3)  # Needs IV = ESI 1-3

    # Signal 5: Pain medications (moderate acuity)
    if "hydrocodone" in medications or "tramadol" in medications:
        base_score = min(base_score, 3)  # Severe pain

    return base_score  # ESI 1-5
```

**Advantages:**
- ✅ No manual SNOMED mapping needed
- ✅ Uses multiple data sources (more robust)
- ✅ Clinically interpretable
- ✅ Covers 100% of patients (no "unknown")

**Disadvantages:**
- ⚠️ Still somewhat rule-based
- ⚠️ Requires tuning weights/thresholds

---

### **Option 2: Unsupervised Clustering**

**Idea:** Let ML discover natural groupings of patient acuity

```python
from sklearn.cluster import KMeans

# Features: demographics + vitals + medication counts + procedure counts
X = [age, gender, hr, spo2, bp, temp, rr,
     num_critical_meds, num_iv_meds, num_procedures]

# Cluster into 5 groups
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(X)

# Map clusters to ESI based on severity of cluster centroids
esi_labels = map_clusters_to_esi(clusters, cluster_centers)
```

**Advantages:**
- ✅ No manual labeling needed
- ✅ Discovers patterns in data

**Disadvantages:**
- ❌ Hard to interpret clinically
- ❌ May not align with real ESI

---

### **Option 3: Use Encounter Outcomes as Proxy** (Careful!)

**Idea:** Use what actually happened to infer initial severity

```python
# Signals from FHIR:
- encounter.class (EMER, IMP, AMB)
- encounter.hospitalization.admitSource
- encounter.hospitalization.dischargeDisposition
- Length of stay (encounter.period.end - start)

# Heuristic:
if encounter.class == "EMER" and length_of_stay > 6 hours:
    esi = 2  # Emergent
elif encounter.class == "EMER":
    esi = 3  # Urgent
elif encounter.class == "IMP":
    esi = 2  # Required admission
elif encounter.class == "AMB":
    esi = 4-5  # Outpatient
```

**Advantages:**
- ✅ Uses actual outcomes
- ✅ No manual coding

**Disadvantages:**
- ⚠️ **Risk of leakage:** Outcome influenced by triage decision
- ⚠️ Not pure "arrival time" signal

**Validation needed:** Check if this creates circular dependencies

---

### **Option 4: Download Real ESI Labels** (If Available)

**Check if dataset has ESI labels already:**

Some FHIR datasets include:
- `Observation` with LOINC code for "Triage acuity"
- Custom extensions with ESI levels

```python
# Search for triage observations
for obs in observations:
    if obs.code.coding.code == "54094-8":  # LOINC for ED triage
        esi_level = obs.valueCodeableConcept.coding.code
```

Let me check our Synthea data for this...

---

### **Option 5: Use ICD-10 Diagnosis Codes**

If reasonCode doesn't have SNOMED, check for diagnosis codes:

```python
# Encounter.diagnosis → Condition resources → ICD-10 codes
# Map common ICD-10 codes to ESI:
icd10_to_esi = {
    "I21": 1,  # Acute MI
    "I63": 1,  # Stroke
    "J44.0": 2,  # COPD exacerbation
    "J18.9": 3,  # Pneumonia
    ...
}
```

**Advantage:** ICD-10 might have better coverage than SNOMED
**Disadvantage:** ICD-10 is assigned post-diagnosis (temporal leakage?)

---

### **Option 6: Train ESI Predictor on Real Hospital Data** (Future)

If we had access to real hospital data with ESI labels:

```python
# Historical data with ground truth ESI
X = [demographics, chief_complaint, vitals, history]
y = [actual_esi_assigned_by_nurse]

# Train XGBoost to predict ESI
esi_model = XGBClassifier()
esi_model.fit(X, y)

# Use on Synthea data
synthea_esi = esi_model.predict(synthea_X)
```

This would learn from **actual triage decisions** made by nurses.

---

## Comparison Matrix

| Approach | Coverage | Clinical Validity | Leakage Risk | Effort |
|----------|----------|-------------------|--------------|--------|
| **SNOMED mapping (current)** | 0.007% | High (if mapped correctly) | Low | High (manual) |
| **Multi-signal composite** | 100% | High (evidence-based) | Low | Medium |
| **Unsupervised clustering** | 100% | Unknown | None | Low |
| **Encounter outcomes** | 100% | Medium | **High** | Low |
| **Real ESI labels (if exist)** | 100% | Perfect | None | Low |
| **ICD-10 mapping** | ~10-20% | Medium-High | Medium | Medium |
| **Learn from hospital data** | 100% | High | None | High (need data) |

---

## Recommendation for Hackathon

**Use Option 1: Multi-Signal Composite Approach**

### Implementation Plan:

1. **Extract additional signals:**
   ```python
   # medications
   features['has_nitroglycerin'] = 1 if "nitroglycerin" in meds else 0
   features['has_albuterol'] = 1 if "albuterol" in meds else 0
   features['has_iv_antibiotics'] = 1 if any("IV" in m for m in meds) else 0

   # procedures
   features['has_intubation'] = 1 if "intubation" in procs else 0
   features['has_iv_placement'] = 1 if "IV" in procs else 0
   ```

2. **Create composite score:**
   ```python
   base_esi = 4  # Default

   # Upgrade based on signals
   if critical_vitals:
       base_esi = min(base_esi, 2)
   if critical_meds:
       base_esi = min(base_esi, 2)
   if emergency_procedure:
       base_esi = min(base_esi, 1)

   # Downgrade if clearly low acuity
   if encounter_type == "checkup" and no_critical_signals:
       base_esi = 5
   ```

3. **Validate against SNOMED where available:**
   - For the 77 patients with SNOMED codes, check if multi-signal agrees
   - Tune weights based on agreement

---

## Next Steps to Explore

1. ✅ Check if Synthea data has triage observations with ESI
2. ✅ Extract medications and procedures from FHIR
3. ✅ Implement multi-signal labeling
4. ✅ Compare multi-signal vs SNOMED-only
5. ✅ Evaluate which gives more realistic ESI distribution

---

## Questions to Answer

1. **Does Synthea include ESI labels in the data already?**
   - Check `Observation` resources for triage codes

2. **What medications/procedures correlate with encounter.class?**
   - Do EMER encounters get more critical meds?

3. **Can we use encounter.class at all without circularity?**
   - Maybe as a **validation signal** not a label source?

4. **What's the ground truth?**
   - In real hospitals, **nurses assign ESI** based on all available info
   - We're trying to approximate that decision

---

Would you like me to implement the multi-signal approach and compare it to SNOMED-only?
