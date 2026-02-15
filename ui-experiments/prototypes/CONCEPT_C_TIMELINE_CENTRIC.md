# UI Concept C: "Timeline-Centric"

## Overview
Timeline-first interface that emphasizes temporal patterns in patient health data. Inspired by "Health Timeline Tool" research showing 90-second review windows enable rapid understanding of patient history, trends, and current state.

**Target User:** Triage master who needs to quickly understand patient trajectory and identify patterns

**Key Principle:** "Context Through Time" - See the patient's health journey at a glance, spot trends instantly

## Core Design Philosophy

- **Timeline as primary navigation** - Patient history unfolds chronologically
- **Visual pattern recognition** - Trends, recurring issues, and escalations visible immediately
- **Temporal context** - "Why now?" answered through recent events
- **Predictive insights** - Past patterns suggest current risk
- **Compressed time view** - Last 90 days on one screen

## Wireframe Layout (Desktop)

### Main View: Patient Timeline

```
┌────────────────────────────────────────────────────────────────────────────┐
│ TRIAGE TIMELINE VIEW             [Hospital Name]  [Search] [🔔] [User]     │
├────────────────────────────────────────────────────────────────────────────┤
│ Current Patient: Rajesh Kumar, 45M | ABHA: 22-7225-4829-5255               │
│ 🔴 CRITICAL - Chest Pain | Arrived: 3 min ago via 🚑 Ambulance             │
├─────────────────┬──────────────────────────────────────────────────────────┤
│                 │                                                           │
│ CURRENT STATUS  │ HEALTH TIMELINE - Last 90 Days                           │
│                 │ ┌─────────────────────────────────────────────────────┐ │
│ BP: 180/110 ⚠  │ │ TODAY           60 Days Ago      30 Days Ago     NOW │ │
│ HR: 125 ⚠      │ │   │                 │                │             │  │ │
│ SpO2: 94% ⚠    │ │   ▼                 ▼                ▼             ▼  │ │
│ Temp: 98.6°F   │ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │
│ RR: 22/min ⚠   │ │                                                       │ │
│                 │ │   🏥 AIIMS                                          🚑│ │
│ ⏱ Wait: 3 min  │ │   Follow-up                                Ambulance │ │
│                 │ │   Post-surgery                              ARRIVAL  │ │
│ 🚑 Ambulance    │ │   check                                     Chest pain││
│ Pre-hospital:   │ │      │                                          │    │ │
│ ✓ ECG done      │ │      │    🏥 Apollo                            │    │ │
│ ✓ Aspirin given │ │      │    Cardiac F/U                          │    │ │
│ ✓ O2 4L/min     │ │      │    Stent check    🧪 Labs       🏥 Apollo   │ │
│                 │ │      │         │         High Chol      Cardio F/U │ │
│ [VIEW AMB ECG]  │ │      │         │            │              │       │ │
│                 │ │      ▼         ▼            ▼              ▼       ▼ │ │
│ CRITICAL ALERTS │ │    Day 60     Day 45      Day 10        Day 2    NOW │ │
│ ⚠ Previous MI   │ └─────────────────────────────────────────────────────┘ │
│   2 years ago   │                                                           │
│ ⚠ Diabetic      │ TIMELINE DETAIL (Click any event to expand)               │
│   On insulin    │ ┌──────────────────────────────────────────────────────┐│
│ ⚠ Allergy:      │ │ TODAY - 10:30 AM - 🚑 Ambulance Arrival              ││
│   Penicillin    │ │ ├─ Chief Complaint: Chest pain, SOB                  ││
│                 │ │ ├─ Vitals: BP 180/110, HR 125, SpO2 94%, RR 22       ││
│ [View All]      │ │ ├─ Treatment Given: Aspirin 325mg, O2 4L/min         ││
│                 │ │ ├─ ECG: ST elevation in leads II, III, aVF           ││
│                 │ │ └─ 📎 Ambulance Report.pdf                           ││
│ MEDICATIONS     │ │                                                       ││
│ Current (5):    │ │ 2 DAYS AGO - 🏥 Apollo Hospital - Cardiology         ││
│ • Metformin     │ │ ├─ Visit Type: Routine follow-up post-MI             ││
│ • Aspirin       │ │ ├─ Vitals: BP 135/85, HR 78, all stable              ││
│ • Atorvastatin  │ │ ├─ ECG: Normal sinus rhythm, no acute changes        ││
│ • Metoprolol    │ │ ├─ Echocardiogram: LVEF 55% (normal function)        ││
│ • Lisinopril    │ │ ├─ Assessment: Recovering well, continue meds        ││
│                 │ │ ├─ Plan: Return in 3 months                          ││
│ [Timeline View] │ │ └─ 📎 Discharge Summary, Echo Report                 ││
│                 │ │                                                       ││
│ CONDITIONS      │ │ 10 DAYS AGO - 🧪 Lab Results (via ABDM)              ││
│ Active (3):     │ │ ├─ Lipid Panel:                                      ││
│ • Type 2 DM     │ │ │  - Total Cholesterol: 245 mg/dL ⚠ HIGH            ││
│ • Hypertension  │ │ │  - LDL: 160 mg/dL ⚠ HIGH                          ││
│ • CAD (s/p MI)  │ │ │  - HDL: 38 mg/dL ⚠ LOW                            ││
│                 │ │ │  - Triglycerides: 235 mg/dL ⚠ HIGH                ││
│ [Full History]  │ │ ├─ HbA1c: 7.2% (Diabetes controlled)                 ││
│                 │ │ ├─ Creatinine: 1.1 mg/dL (Normal kidney function)    ││
│                 │ │ └─ Liver function: Normal                            ││
│ DATA SOURCES    │ │                                                       ││
│ ✓ Ambulance     │ │ 45 DAYS AGO - 🏥 Apollo Hospital - Cardiology        ││
│ ✓ Apollo (ABDM) │ │ ├─ Visit: 6-month post-stent check                   ││
│ ✓ AIIMS (ABDM)  │ │ ├─ Angiography: Stent patent, good flow              ││
│ ✓ Labs (ABDM)   │ │ ├─ Assessment: Excellent recovery                    ││
│ ✓ Pharmacy      │ │ └─ Continue current medications                      ││
│                 │ │                                                       ││
│ [Fetch More]    │ │ 60 DAYS AGO - 🏥 AIIMS - Post-Op Follow-Up           ││
│                 │ │ ├─ Visit: 2 weeks post CABG surgery                  ││
│                 │ │ ├─ Vitals: Stable, wound healing well                ││
│                 │ │ ├─ Started cardiac rehab program                     ││
│                 │ │ └─ Referred to Apollo for local cardiology care      ││
│                 │ │                                                       ││
│                 │ │ [Load Earlier History (2 years available)]           ││
│                 │ └──────────────────────────────────────────────────────┘│
│                 │                                                           │
│                 │ TREND ANALYSIS                                            │
│                 │ ┌──────────────────────────────────────────────────────┐│
│                 │ │ 📊 VITAL SIGNS TRENDS (Last 90 Days)                 ││
│                 │ │                                                       ││
│                 │ │ Blood Pressure:                                       ││
│                 │ │ 200├─────────────────────────────────────            ││
│                 │ │ 180├─────────────────────────────────▲ 180/110 (NOW) ││
│                 │ │ 160├──────────────────────────────────               ││
│                 │ │ 140├────────────────────────────────                 ││
│                 │ │ 120├────●────────●────────●────────                  ││
│                 │ │ 100└────┬────────┬────────┬────────┬                 ││
│                 │ │      60d     45d     30d     10d   NOW              ││
│                 │ │                                                       ││
│                 │ │ ⚠ PATTERN: Sudden spike today vs stable 90 days      ││
│                 │ │ ⚠ RISK: Indicates acute cardiac event                ││
│                 │ │                                                       ││
│                 │ │ Cholesterol Trend:                                    ││
│                 │ │ ↗ Increasing despite medication (245 → concerning)   ││
│                 │ │                                                       ││
│                 │ │ HbA1c Trend:                                          ││
│                 │ │ → Stable 7.2% (diabetes under control)               ││
│                 │ └──────────────────────────────────────────────────────┘│
│                 │                                                           │
│                 │ PREDICTIVE INSIGHTS                                       │
│                 │ ┌──────────────────────────────────────────────────────┐│
│                 │ │ 🤖 AI RISK ASSESSMENT                                ││
│                 │ │                                                       ││
│                 │ │ LIKELY DIAGNOSIS: Acute MI (STEMI)                   ││
│                 │ │ Confidence: 92%                                       ││
│                 │ │                                                       ││
│                 │ │ SUPPORTING EVIDENCE:                                  ││
│                 │ │ ✓ ECG: ST elevation (ambulance report)               ││
│                 │ │ ✓ Symptoms: Chest pain + SOB (classic presentation)  ││
│                 │ │ ✓ History: Previous MI 2 years ago (recurrence risk) ││
│                 │ │ ✓ Risk factors: Diabetes, high cholesterol, HTN      ││
│                 │ │ ✓ Acute onset: 30 min ago (timing consistent)        ││
│                 │ │                                                       ││
│                 │ │ RECOMMENDED ACTIONS:                                  ││
│                 │ │ 1. Code STEMI activation                              ││
│                 │ │ 2. Cath lab notification                              ││
│                 │ │ 3. STAT troponin, repeat ECG                          ││
│                 │ │ 4. Cardiology consult within 15 minutes               ││
│                 │ │ 5. Transfer to critical care bay                      ││
│                 │ │                                                       ││
│                 │ │ SIMILAR CASES: 47 in last year (avg door-to-balloon: ││
│                 │ │ 62 min)                                               ││
│                 │ └──────────────────────────────────────────────────────┘│
├─────────────────┴──────────────────────────────────────────────────────────┤
│ QUICK ACTIONS                                                               │
│ [🚨 ACTIVATE CODE STEMI] [📞 CALL CARDIOLOGY] [🧪 ORDER STAT LABS]        │
│ [🛏️ ASSIGN CRITICAL BAY] [📄 REQUEST FULL ABDM HISTORY] [📋 TRIAGE NOTES]│
└────────────────────────────────────────────────────────────────────────────┘
```

## Alternative Timeline Visualization: Horizontal Swim Lanes

```
┌────────────────────────────────────────────────────────────────────────────┐
│ MULTI-DIMENSIONAL TIMELINE VIEW                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Timeline: Last 90 Days for Rajesh Kumar, 45M                               │
│                                                                             │
│ ┌───────────────────────────────────────────────────────────────────────┐ │
│ │ ENCOUNTERS   │                                                         │ │
│ │ 🏥           │    ●────────────●──────────────●─────────●─────────●   │ │
│ │              │   AIIMS      Apollo        Apollo    Apollo   Apollo   │ │
│ │              │  Surgery    Cardio F/U    Stent Chk  Cardio   Cardio   │ │
│ ├──────────────┼─────────────────────────────────────────────────────────│ │
│ │ LAB RESULTS  │                                                         │ │
│ │ 🧪           │              ●─────────────────●                        │ │
│ │              │          Post-op labs      Lipid panel                  │ │
│ ├──────────────┼─────────────────────────────────────────────────────────│ │
│ │ MEDICATIONS  │ ═══════════════════════════════════════════════════════ │ │
│ │ 💊           │ [Metformin, Aspirin, Statin, BP meds - continuous]      │ │
│ │              │    ▲ Initiated                           ▲ Refilled    │ │
│ ├──────────────┼─────────────────────────────────────────────────────────│ │
│ │ VITAL SIGNS  │          ↑↑                  ↑      →    →    ↑↑↑      │ │
│ │ 📊           │         BP spike         Stable   Stable  BP crisis    │ │
│ ├──────────────┼─────────────────────────────────────────────────────────│ │
│ │ EVENTS       │                                               🚑        │ │
│ │ 🚨           │                                           Ambulance     │ │
│ │              │                                           (NOW)         │ │
│ └──────────────┴─────────────────────────────────────────────────────────┘ │
│                 │         │         │         │         │                  │
│              90 days   60 days   45 days   30 days   TODAY                 │
│                                                                             │
│ Click any event to see details ↓                                           │
│                                                                             │
│ Selected: TODAY - Ambulance Arrival                                        │
│ [Full details shown in panel below...]                                     │
└────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Temporal Context at a Glance

**The "Why Now?" Question:**
- Visual timeline shows patient was recently seen (2 days ago, stable)
- Sudden change indicates acute event (not chronic deterioration)
- Pattern: Regular follow-ups → Compliant patient
- Lab trends: Cholesterol worsening despite meds → Risk factor

**90-Second Review Window:**
```
0-10s:  Scan visual timeline (encounters, labs, vitals)
10-30s: Read recent events (last 7-10 days in detail)
30-50s: Check trend analysis (BP, labs, compliance)
50-70s: Review AI insights and recommendations
70-90s: Make triage decision based on complete context
```

### 2. Visual Pattern Recognition

**Color Coding for Event Types:**
- 🔴 **Critical Events:** Red markers (MI, stroke, major surgery)
- 🟡 **Important Events:** Amber markers (urgent visits, abnormal labs)
- 🟢 **Routine Events:** Green markers (follow-ups, refills)
- 🔵 **Preventive:** Blue markers (screenings, vaccinations)

**Visual Density Indicates:**
- **Dense cluster of events:** Complex/sick patient, frequent healthcare use
- **Sparse events:** Generally healthy, infrequent care
- **Recent cluster after gap:** Acute change or new diagnosis
- **Regular spacing:** Chronic condition management (good compliance)

### 3. Trend Visualization

**Built-in Charts:**
```javascript
// Auto-generate trend charts from FHIR data

Vital Signs:
- Blood Pressure over time
- Weight trends (diabetes, CHF monitoring)
- SpO2 for respiratory patients
- Blood glucose for diabetics

Lab Results:
- HbA1c trends (diabetes control)
- Creatinine (kidney function)
- Lipid panel (cardiac risk)
- Liver enzymes (if on meds)

Medication Adherence:
- Timeline of fills/refills
- Gaps = non-adherence
- Continuous = compliant
```

**Anomaly Detection:**
```
VISUAL ALERTS:

⚠ Sudden BP spike (was 135/85, now 180/110)
  → Red highlight + annotation

⚠ Missed appointment (gap in expected follow-up)
  → Yellow flag on timeline

⚠ Medication gap (no refill for 60 days)
  → Dashed line in medication lane

✓ Improving trend (HbA1c: 8.5 → 7.2 → 7.0)
  → Green upward arrow
```

### 4. Multi-Source Data Integration

**Timeline Shows ALL Sources:**
```
TODAY:
🚑 Ambulance: Pre-hospital data (real-time)

RECENT (Last 7 days):
🏥 Apollo Hospital: Cardio follow-up (ABDM)
🧪 Lab Results: Cholesterol panel (ABDM)
💊 Pharmacy: Medication refill (local database)

HISTORICAL (Last 90 days):
🏥 Apollo: Multiple cardio visits (ABDM)
🏥 AIIMS: Post-surgery care (ABDM request if not cached)
📱 Patient App: Self-reported BP readings (if available)

DEEP HISTORY (> 90 days, on demand):
🏥 All encounters from all linked HIPs
📊 Complete lab history
💊 Full medication history
🏥 Imaging reports (FHIR DocumentReference)
```

**Data Freshness Indicators:**
- Real-time (< 5 min): ⚡ Lightning bolt icon
- Recent (< 24 hours): ✓ Green checkmark
- Current (< 7 days): Blue dot
- Historical (> 7 days): Gray text
- Stale (> 90 days): Faded, collapsed by default

### 5. Predictive AI Insights

**Powered by Timeline Data:**
```python
# Conceptual AI analysis using timeline context

def generate_triage_insights(timeline_data):
    """
    Analyze patient timeline to predict:
    - Likely diagnosis
    - Risk level
    - Recommended actions
    - Similar case outcomes
    """

    features = extract_timeline_features(timeline_data)

    # Feature engineering:
    - Time since last similar event
    - Frequency of ED visits (frequent flyer?)
    - Medication compliance (gaps in refills)
    - Lab trend direction (improving/worsening)
    - Symptom recurrence patterns

    # ML model inference:
    prediction = triage_ml_model.predict(features)

    return {
        "diagnosis": "Acute MI (STEMI)",
        "confidence": 0.92,
        "risk_level": "CRITICAL",
        "recommended_actions": [
            "Activate Code STEMI",
            "Cath lab notification",
            "STAT troponin, ECG"
        ],
        "similar_cases": 47,
        "avg_outcome": "door-to-balloon 62 min"
    }
```

**Evidence-Based Suggestions:**
- Not black box: Shows WHY AI thinks this
- Highlights supporting timeline evidence
- Links to similar past cases
- Suggests protocol-based actions

### 6. ABDM Integration (Timeline-Focused)

**Fetch Strategy:**
```python
# When patient identified, fetch comprehensive timeline:

async def build_patient_timeline(abha_number):
    """
    Fetch and merge data from all ABDM HIPs
    into unified timeline view
    """

    # 1. Discover all linked HIPs
    hips = await abdm_client.discover_patient(abha_number)

    # 2. Request consent for all HIPs (emergency streamlined)
    consents = await asyncio.gather(*[
        abdm_client.request_emergency_consent(
            hip.id,
            hi_types=["DiagnosticReport", "Prescription",
                      "DischargeSummary", "OPConsultation",
                      "ImmunizationRecord", "WellnessRecord"],
            lookback_days=90  # Last 90 days for timeline
        )
        for hip in hips
    ])

    # 3. Fetch all records in parallel
    all_records = await asyncio.gather(*[
        abdm_client.fetch_health_information(consent.id)
        for consent in consents
    ])

    # 4. Parse FHIR bundles into timeline events
    timeline_events = []
    for hip_records in all_records:
        for record in hip_records:
            bundle = Bundle.parse_obj(record)
            events = extract_timeline_events(bundle)
            timeline_events.extend(events)

    # 5. Sort by timestamp (most recent first)
    timeline_events.sort(key=lambda e: e.timestamp, reverse=True)

    # 6. Detect trends and patterns
    trends = analyze_trends(timeline_events)

    # 7. Generate AI insights
    insights = generate_insights(timeline_events, trends)

    return {
        "events": timeline_events,
        "trends": trends,
        "insights": insights
    }

def extract_timeline_events(bundle):
    """
    Convert FHIR bundle into timeline-friendly events
    """
    events = []

    for entry in bundle.entry:
        resource = entry.resource

        if resource.resource_type == "Encounter":
            events.append({
                "type": "encounter",
                "timestamp": resource.period.start,
                "title": f"{resource.type[0].text} at {get_org_name(bundle)}",
                "details": resource.reasonCode,
                "icon": "🏥"
            })

        elif resource.resource_type == "DiagnosticReport":
            events.append({
                "type": "lab",
                "timestamp": resource.effectiveDateTime,
                "title": resource.code.text,
                "results": extract_observations(bundle, resource),
                "icon": "🧪"
            })

        elif resource.resource_type == "MedicationRequest":
            events.append({
                "type": "medication",
                "timestamp": resource.authoredOn,
                "title": resource.medicationCodeableConcept.text,
                "dosage": resource.dosageInstruction[0].text,
                "icon": "💊"
            })

        # ... handle other FHIR resource types

    return events
```

### 7. Quick Navigation

**Timeline Shortcuts:**
```
ZOOM LEVELS:
[24 hours] [7 days] [30 days] [90 days] [1 year] [All]

FILTERS:
[All Events] [Encounters Only] [Labs Only] [Meds Only] [Critical Only]

JUMP TO:
- Last ED visit
- Last hospitalization
- Most recent labs
- Medication changes

HIGHLIGHT:
- Cardiac events (for this patient's chest pain)
- Diabetes-related (for diabetic patients)
- All abnormal results
```

**Keyboard Shortcuts:**
```
← → : Navigate timeline left/right
↑ ↓ : Zoom in/out (change time scale)
Space: Expand/collapse selected event
Enter: Open full details
Esc: Close details, return to overview
/: Search timeline
```

## Mobile Adaptation

**Timeline on Mobile (Vertical Scroll):**
```
┌─────────────────────────────────────┐
│ ←  Rajesh Kumar Timeline       [⋮] │
├─────────────────────────────────────┤
│                                      │
│ ━━━━━━━━ TODAY ━━━━━━━━             │
│                                      │
│ 🚑 10:30 AM - Ambulance Arrival     │
│ ┌──────────────────────────────────┐│
│ │ Chest pain, SOB                  ││
│ │ BP 180/110, HR 125, SpO2 94%    ││
│ │ ECG: ST elevation                ││
│ │ [View ambulance ECG]             ││
│ └──────────────────────────────────┘│
│                                      │
│ ━━━━━━ 2 DAYS AGO ━━━━━━            │
│                                      │
│ 🏥 Apollo Hospital - Cardiology     │
│ ┌──────────────────────────────────┐│
│ │ Routine follow-up                ││
│ │ All stable, continue meds        ││
│ │ [View discharge summary]         ││
│ └──────────────────────────────────┘│
│                                      │
│ ━━━━━━ 10 DAYS AGO ━━━━━━           │
│                                      │
│ 🧪 Lab Results (ABDM)               │
│ ┌──────────────────────────────────┐│
│ │ Cholesterol: 245 ⚠ HIGH          ││
│ │ HbA1c: 7.2% → Controlled         ││
│ │ [View full panel]                ││
│ └──────────────────────────────────┘│
│                                      │
│ ━━━━━ 45 DAYS AGO ━━━━━             │
│                                      │
│ 🏥 Apollo - Stent Check             │
│ [Tap to expand...]                   │
│                                      │
│ ━━━━━ 60 DAYS AGO ━━━━━             │
│                                      │
│ 🏥 AIIMS - Post-Op Follow-Up        │
│ [Tap to expand...]                   │
│                                      │
│ [Load earlier events...]             │
│                                      │
│                                      │
│ ┌─ TRENDS & INSIGHTS ─────────────┐│
│ │ 📊 BP: Sudden spike today        ││
│ │ ⚠ Risk: Acute cardiac event      ││
│ │ [View AI analysis]               ││
│ └──────────────────────────────────┘│
│                                      │
├─────────────────────────────────────┤
│ [TRIAGE] [CALL CARDIO] [STAT LABS] │
└─────────────────────────────────────┘
```

## Data Visualization Components

### Component Library Needed:
```javascript
// Timeline visualization components

import {
  TimelineView,         // Main horizontal timeline
  TimelineEvent,        // Individual event marker
  SwimLane,             // Multi-track timeline
  TrendChart,           // Line/area charts for vitals
  EventDetail,          // Expandable event panel
  TimelineFilter,       // Filter by event type
  ZoomControl,          // Timeline zoom (hours to years)
  AnomalyHighlight,     // Visual alert for pattern breaks
  AIInsightPanel        // Predictive insights display
} from '@/components/timeline'

// Chart library: Recharts or D3.js for custom viz
// Date handling: date-fns for lightweight date manipulation
```

## Strengths of This Concept

✅ **Context-Rich:** See full patient journey instantly
✅ **Pattern Recognition:** Trends and anomalies visually obvious
✅ **Evidence-Based:** AI suggestions backed by timeline data
✅ **Predictive:** Past patterns inform current risk assessment
✅ **Comprehensive:** All data sources in unified view
✅ **Educational:** Helps train junior staff to think longitudinally

## Limitations

❌ **Data-Dependent:** Requires rich historical data (not great for new patients)
❌ **Complexity:** Steep learning curve for timeline navigation
❌ **Performance:** Rendering long timelines (years of data) can be slow
❌ **Single-Patient Focus:** Less effective for queue management
❌ **Screen Real Estate:** Needs horizontal space for timeline

## When to Use Timeline-Centric

**Ideal for:**
- Complex patients with extensive medical history
- Chronic disease management (diabetes, CHF, COPD)
- Understanding recurrent symptoms/admissions
- Teaching hospitals (educational value)
- Identifying medication compliance issues
- Spotting deterioration trends early

**Not ideal for:**
- Brand new patients (minimal history)
- Mass casualty/disaster triage (too slow)
- Simple acute injuries (minor trauma)
- Queue management (focus is depth, not breadth)

## User Testing Metrics

**Success Criteria:**
- Time to diagnosis: < 90 seconds (with rich history)
- Pattern identification: > 80% accuracy
- User preference: > 60% prefer timeline vs traditional
- AI insight accuracy: > 85% match physician diagnosis
- Trend chart comprehension: > 90% understand at a glance

## Technical Considerations

**Performance Optimization:**
```javascript
// Virtual scrolling for long timelines
import { FixedSizeList } from 'react-window'

// Lazy load event details (only fetch when expanded)
const EventDetail = lazy(() => import('./EventDetail'))

// Memoize expensive timeline calculations
const timeline = useMemo(() =>
  buildTimeline(events, filters, zoomLevel),
  [events, filters, zoomLevel]
)

// Debounce zoom/pan interactions
const handleZoom = useDebouncedCallback(
  (newZoomLevel) => setZoomLevel(newZoomLevel),
  150
)
```

**Data Caching:**
```javascript
// Cache timeline data to avoid re-fetching
import { QueryClient } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 minutes
      cacheTime: 30 * 60 * 1000,  // 30 minutes
    },
  },
})

// Pre-fetch timeline data for critical patients
queryClient.prefetchQuery({
  queryKey: ['timeline', patient.abha],
  queryFn: () => fetchPatientTimeline(patient.abha)
})
```

## Next Steps

1. **Interactive prototype** with mock timeline data
2. **User testing** with clinicians (observe comprehension speed)
3. **AI model training** on real patient timelines
4. **Performance testing** with varying data volumes
5. **A/B test** against traditional list view
