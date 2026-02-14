# UI Concept A: "Command Center"

## Overview
Dashboard-centric interface optimized for managing multiple patients simultaneously with real-time monitoring. Inspired by emergency department information systems and queue management research.

**Target User:** Triage master managing 20-40 patients across different acuity levels simultaneously

**Key Principle:** "All in One" - Single-screen view with minimal navigation

## Core Design Philosophy

- **Grid-based layout** with color-coded patient cards
- **Real-time updates** for vital signs and queue status
- **Parallel monitoring** of critical cases while managing queue
- **Quick actions** without leaving dashboard

## Wireframe Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│ EMERGENCY TRIAGE COMMAND CENTER                    [Hospital Name] [User]  │
│ [Search ABHA/Name/Phone] [🔔 Alerts: 2] [Settings] [Logout]               │
├────────────────────────────────────────────────────────────────────────────┤
│ DEPARTMENT STATUS                                    Last Updated: 10:34   │
│ ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐       │
│ │   RED    │  YELLOW  │  GREEN   │   BLUE   │  TOTAL   │ AVG WAIT │       │
│ │    3     │    12    │    8     │    5     │  28/45   │  15 min  │       │
│ │ CRITICAL │  URGENT  │  MINOR   │   TREAT  │ CAPACITY │          │       │
│ └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ CRITICAL ATTENTION REQUIRED (RED) - 3 Patients                             │
│ ┌──────────────────────────────────────────────────────────────────────┐  │
│ │ 🔴 Rajesh Kumar, 45M │ ABHA: **-5255 │ ⏱ 3m │ 🚑 Ambulance │ BP↑ HR↑│  │
│ │ Chief Complaint: Chest pain, SOB                                     │  │
│ │ Vitals: BP 180/110 HR 125 SpO2 94% │ 🩺 Cardiac Hx │ 💊 3 Current   │  │
│ │ [VIEW FULL] [ASSIGN BAY] [CALL CARDIO] [ECG ORDER]                  │  │
│ └──────────────────────────────────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────────────────────────────────┐  │
│ │ 🔴 Priya Sharma, 28F │ ABHA: **-7891 │ ⏱ 7m │ 🚗 Walk-in │ RR↑ Temp↑│  │
│ │ Chief Complaint: Severe abdominal pain, vomiting                     │  │
│ │ Vitals: BP 90/60 HR 110 Temp 102°F │ ⚠ Pregnant (12w) │ No Meds     │  │
│ │ [VIEW FULL] [ASSIGN BAY] [CALL OB/GYN] [LAB ORDER]                  │  │
│ └──────────────────────────────────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────────────────────────────────┐  │
│ │ 🔴 Anil Patel, 62M │ ABHA: **-3421 │ ⏱ 12m │ 🚑 Ambulance │ BP↓ SpO2↓│  │
│ │ Chief Complaint: Altered mental status, weakness                     │  │
│ │ Vitals: BP 85/50 HR 95 SpO2 88% │ 🩺 Diabetes, CVD │ 💊 7 Current   │  │
│ │ [VIEW FULL] [ASSIGN BAY] [CALL NEURO] [STAT LABS]                   │  │
│ └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│ URGENT (YELLOW) - 12 Patients           [▼ Expand All] [Filter by Time ⏱] │
│ ┌────────────────────────────────────────────────────────────────────┐    │
│ │ 🟡 Meena Singh, 35F │ ⏱ 18m │ Fever 3 days, rash   │ [VIEW] [ASSIGN] │ │
│ │ 🟡 Arjun Das, 52M   │ ⏱ 22m │ Right knee pain      │ [VIEW] [ASSIGN] │ │
│ │ 🟡 Lakshmi Reddy, 41F│⏱ 25m │ Migraine, vomiting   │ [VIEW] [ASSIGN] │ │
│ │ [▼ Show 9 more patients...]                                          │ │
│ └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│ MINOR (GREEN) - 8 Patients              [▼ Expand All] [Filter by Time ⏱] │
│ ┌────────────────────────────────────────────────────────────────────┐    │
│ │ 🟢 Ravi Kumar, 22M  │ ⏱ 35m │ Minor laceration    │ [VIEW] [ASSIGN] │ │
│ │ 🟢 Sunita Joshi, 30F│ ⏱ 40m │ Cold symptoms       │ [VIEW] [ASSIGN] │ │
│ │ [▼ Show 6 more patients...]                                          │ │
│ └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│ IN TREATMENT (BLUE) - 5 Patients        [▼ View All]                       │
└────────────────────────────────────────────────────────────────────────────┘

FOOTER STATUS BAR:
[🔴 Live] [Network: Connected] [ABDM: Online] [Last Sync: 10:34:12]
```

## Detailed Patient View (Modal/Slide-in from Right)

When clicking "[VIEW FULL]" on any patient:

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard              PATIENT DETAIL                        [X] │
├────────────────────────────────────────────────────────────────────────────┤
│ Rajesh Kumar | 45M | ABHA: 22-7225-4829-5255                               │
│ 🔴 CRITICAL - Chest Pain | Arrived: 3 min ago via 🚑 Ambulance             │
│ Mobile: +91-9876543210 | Address: Koramangala, Bangalore                   │
├──────────────────────┬─────────────────────────────────────────────────────┤
│ VITAL SIGNS          │ ┌──────────────────────────────────────────────┐   │
│ (Real-time Stream)   │ │ 🫀 BP: 180/110 mmHg ⚠ CRITICAL              │   │
│                      │ │    Last: 2m ago  Trend: ↑ Increasing        │   │
│ Ambulance Report:    │ │                                              │   │
│ ✓ ECG in transit     │ │ 💓 Heart Rate: 125 bpm ⚠ HIGH               │   │
│ ✓ Given Aspirin      │ │    Last: 2m ago  Trend: → Stable            │   │
│ ✓ O2 started 4L/min  │ │                                              │   │
│                      │ │ 🫁 SpO2: 94% ⚠ LOW                          │   │
│ [VIEW AMBULANCE ECG] │ │    Last: 2m ago  Trend: ↓ Decreasing        │   │
│                      │ │                                              │   │
│                      │ │ 🌡️ Temperature: 98.6°F ✓ Normal             │   │
│                      │ │                                              │   │
│                      │ │ 🫁 Respiratory Rate: 22 /min ⚠ ELEVATED     │   │
│                      │ └──────────────────────────────────────────────┘   │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ CRITICAL ALERTS      │ ⚠ ACTIVE CARDIAC HISTORY                            │
│                      │   • Previous MI (Myocardial Infarction) 2 years ago│
│                      │   • Stent placement: LAD artery (2024)              │
│ [!] 3 Active         │                                                     │
│                      │ ⚠ ALLERGY ALERT                                     │
│                      │   • Penicillin - Anaphylaxis risk                   │
│                      │                                                     │
│                      │ ⚠ DIABETIC - TYPE 2                                 │
│                      │   • On insulin therapy                              │
│                      │   • Last HbA1c: 7.2% (3 weeks ago)                  │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ CURRENT MEDICATIONS  │ • Metformin 500mg BD (Diabetes control)             │
│ (ABDM via Apollo)    │ • Aspirin 75mg OD (Cardioprotective)                │
│ Last updated: 2d ago │ • Atorvastatin 20mg OD (Cholesterol)                │
│                      │ • Metoprolol 25mg BD (BP control)                   │
│ [VIEW FULL Rx HISTORY]│ • Lisinopril 10mg OD (BP control)                  │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ DATA SOURCES         │ RECENT MEDICAL HISTORY (Last 7 Days)                │
│                      │ Timeline View:                                      │
│ 🚑 Ambulance (3m ago)│ ├─ TODAY 10:30 AM - Ambulance Arrival              │
│ ✓ Pre-hospital data  │ │  └─ Vitals: BP 180/110, HR 125, chest pain      │
│                      │ │  └─ Given: Aspirin 325mg, O2 4L/min              │
│ 🏥 Apollo Hospital   │ │  └─ ECG: ST elevation noted                      │
│ ✓ ABDM connected     │ ├─ 2 DAYS AGO - Apollo Hospital (Cardiology)      │
│ Last visit: 2d ago   │ │  ├─ Follow-up: Post-MI care                      │
│                      │ │  ├─ ECG: Normal sinus rhythm                      │
│ 🧪 Lab Results       │ │  ├─ Echo: LVEF 55% (normal)                       │
│ Last: 3 days ago     │ │  └─ Advised: Continue medications, diet, exercise│
│ ✓ Available          │ ├─ 3 DAYS AGO - Lab Results (ABDM)                │
│                      │ │  ├─ Lipid Panel: Total Chol 245 mg/dL ⚠ HIGH    │
│ 💊 Pharmacy          │ │  ├─ HbA1c: 7.2% (Diabetes controlled)             │
│ ✓ Rx database linked │ │  ├─ Creatinine: 1.1 mg/dL (Normal)               │
│                      │ │  └─ Liver function: Normal                        │
│                      │ └─ 1 WEEK AGO - Pharmacy (Medication Refill)       │
│                      │    └─ Filled: All current medications                │
│                      │                                                     │
│                      │ [VIEW COMPLETE EMR (Last 2 Years)]                  │
├──────────────────────┴─────────────────────────────────────────────────────┤
│ QUICK ACTIONS                                                               │
│ ┌──────────────┬──────────────┬──────────────┬──────────────┬────────────┐│
│ │ 🩺 ASSIGN    │ 📞 CALL      │ 🧪 ORDER     │ 💊 PRESCRIBE │ 📋 NOTES   ││
│ │ ESI LEVEL    │ SPECIALIST   │ TESTS        │ MEDICATION   │            ││
│ └──────────────┴──────────────┴──────────────┴──────────────┴────────────┘│
│ ┌──────────────┬──────────────┬──────────────┬──────────────┬────────────┐│
│ │ 🛏️ ASSIGN    │ 🔔 ALERT     │ 📄 REQUEST   │ 🔄 REFRESH   │ 📤 HANDOFF ││
│ │ TO BAY       │ TEAM         │ CONSENT      │ DATA         │ TO PHYSICIAN││
│ └──────────────┴──────────────┴──────────────┴──────────────┴────────────┘│
└────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Real-Time Dashboard
- **Live queue monitoring** with patient count by acuity
- **Department capacity** tracking (28/45 beds)
- **Average wait time** calculation
- **Auto-refresh** every 10 seconds

### 2. Color-Coded Priority System
Following AIIMS Triage Protocol (ATP):
- 🔴 **RED (Critical):** Immediate life-threatening conditions
- 🟡 **YELLOW (Urgent):** Serious but stable, needs care within 30-60 min
- 🟢 **GREEN (Minor):** Non-urgent, can wait 60+ min
- 🔵 **BLUE (In Treatment):** Currently being treated

### 3. Progressive Disclosure
- **Level 1 (Dashboard Card):** Name, age, ABHA (last 4), time, chief complaint, critical vitals
- **Level 2 (Expanded Card):** Full vitals, alerts, current meds, quick actions
- **Level 3 (Full Detail Modal):** Complete timeline, all data sources, full EMR access

### 4. Multi-Source Data Integration

**ABDM DevKit Integration:**
```python
# Conceptual workflow when patient arrives:

1. IDENTIFY PATIENT
   - Scan ABHA card or manual entry
   - Search by phone/demographics if no ABHA

2. AUTO-FETCH DATA (Background)
   client = ABDMClient(base_url="http://localhost:8090")

   # Discover patient across HIPs
   discovery = await client.hip.discover_patient(
       abha_number="22-7225-4829-5255@sbx"
   )

   # Request consent (emergency access - streamlined)
   consent = await client.hiu.request_consent(
       patient_abha="22-7225-4829-5255@sbx",
       purpose="CAREMGT",  # Care Management
       hi_types=["DiagnosticReport", "Prescription",
                 "DischargeSummary", "OPConsultation"],
       date_range=(30_days_ago, today),
       emergency=True  # Emergency access flag
   )

   # Fetch health records (if consent approved)
   records = await client.hiu.fetch_health_information(
       consent_id=consent.id
   )

3. PARSE FHIR BUNDLES
   from fhir.resources.bundle import Bundle

   for record in records:
       bundle = Bundle.parse_obj(record)

       # Extract for UI display:
       - Conditions (diagnoses)
       - Medications (current prescriptions)
       - Observations (vitals, labs)
       - Procedures (surgeries, interventions)
       - AllergyIntolerances
       - Encounters (recent visits)

4. DISPLAY IN TIMELINE
   - Sort by date/time
   - Group by source (Apollo, AIIMS, etc.)
   - Highlight critical information
   - Show data freshness
```

**Data Source Indicators:**
- 🚑 **Ambulance:** Pre-hospital data (vitals in transit, interventions)
- 🏥 **ABDM HIPs:** Historical records from other hospitals
- 🧪 **Lab Systems:** Recent test results
- 💊 **Pharmacy:** Current medications
- 📱 **Patient App:** Self-reported symptoms, wearable data

### 5. Quick Actions (1-2 Clicks)
All critical actions accessible without scrolling:
- **Assign ESI Level:** 1-5 triage priority
- **Assign to Bay:** Direct patient to treatment area
- **Call Specialist:** Auto-dial cardiology/neurology/etc.
- **Order Tests:** STAT labs, imaging (pre-populated based on complaint)
- **Request Consent:** If ABDM data not auto-fetched
- **Handoff to Physician:** Transfer with complete triage package

### 6. Alert System (Anti-Fatigue Design)

**Hard Stop Alerts (Modal, Must Acknowledge):**
- Known drug allergy with current order
- Critical vital signs (BP <80/40 or >200/120, SpO2 <85%)

**High Priority Alerts (Red banner, dismissable):**
- Recent hospitalization (last 48 hours)
- Active cardiac/respiratory/neurological condition
- Pregnancy with concerning symptoms

**Medium Priority Alerts (Yellow inline badge):**
- Missing medication information
- Data conflict between sources
- Recommended protocol not followed

**Low Priority Alerts (Blue number badge):**
- Additional records available from other HIPs
- Patient has scheduled follow-up

### 7. Performance Targets

**Speed Requirements:**
- Dashboard load: < 2 seconds
- Patient detail view: < 500ms
- ABDM data fetch: < 3 seconds (background, shows loading state)
- Real-time vital update: < 2 seconds
- Search/filter: < 200ms

**60-90 Second Assessment Flow:**
1. Patient card appears automatically (0s)
2. Click patient → Detail opens (0.5s elapsed)
3. Scan vitals + alerts (10s elapsed)
4. Review timeline (30s elapsed)
5. Check medications (45s elapsed)
6. Assess complaint + history (70s elapsed)
7. Assign triage level + bay (75s elapsed)
8. Click handoff (80s elapsed)
9. Add quick note if needed (90s elapsed)

**Total:** Patient triaged in 90 seconds or less

## Technology Stack (Frontend)

```javascript
// Proposed stack for Command Center UI

Framework: React 18+ with TypeScript
State Management: Zustand (lightweight, fast)
Real-time: Socket.io client (for vital signs streaming)
Data Fetching: React Query (with auto-refresh)
UI Components: Shadcn/ui (Tailwind-based, accessible)
Charts: Recharts (for vital trends)
Date/Time: date-fns (lightweight)
Notifications: React Hot Toast

// Example component structure:
src/
  components/
    dashboard/
      TriageDashboard.tsx         # Main view
      PatientCard.tsx              # Collapsible card
      PatientDetailModal.tsx       # Full patient view
      DepartmentStatus.tsx         # Capacity bar
      AlertBanner.tsx              # Critical notifications
    patient/
      VitalSignsPanel.tsx          # Real-time vitals
      TimelineView.tsx             # Medical history timeline
      MedicationList.tsx           # Current medications
      AlertsList.tsx               # Patient-specific alerts
      DataSourceBadges.tsx         # Show data origins
    actions/
      QuickActionsBar.tsx          # 1-click operations
      AssignToBay.tsx              # Bay assignment
      OrderTestsModal.tsx          # Test ordering
  hooks/
    useRealtimeVitals.ts           # Socket.io connection
    useABDMPatientData.ts          # Fetch FHIR data
    useTriageQueue.ts              # Queue management
  services/
    abdmClient.ts                  # SDK integration
    fhirParser.ts                  # Parse FHIR bundles
  types/
    patient.ts                     # TypeScript interfaces
    triage.ts
    fhir.ts
```

## Mobile Responsiveness

**Tablet (iPad) Optimization:**
```
Portrait Mode (768px):
- Stack RED patients vertically (full width)
- YELLOW/GREEN collapsed by default
- Patient detail: Full-screen modal

Landscape Mode (1024px):
- Split view: Queue (60%) + Detail (40%) side-by-side
- RED patients always visible
```

**Phone (Not Primary Use Case, Emergency Fallback):**
```
- Single-column layout
- Bottom navigation for quick actions
- Simplified card view
- Swipe for detail
```

## Accessibility

- **WCAG 2.1 AA Compliant**
- **Keyboard Navigation:** Tab through patients, Enter to open detail
- **Screen Reader:** ARIA labels on all interactive elements
- **Color Contrast:** 4.5:1 minimum for text
- **Focus Indicators:** 2px solid border on focused elements
- **Text Scaling:** Support up to 200% zoom

## Strengths of This Concept

✅ **Parallel Monitoring:** See multiple critical patients at once
✅ **Minimal Context Switching:** Most actions on single screen
✅ **Clear Visual Hierarchy:** RED patients impossible to miss
✅ **Real-Time Awareness:** Live updates for vitals and queue
✅ **Fast Triage:** Optimized for 60-90 second workflow
✅ **Scalable:** Handles 20-40 patients efficiently

## Limitations

❌ **Desktop-First:** Not ideal for mobile-only workflows
❌ **Information Density:** Can feel overwhelming initially
❌ **Screen Real Estate:** Requires large display (24"+ ideal)
❌ **Learning Curve:** More features = more to learn

## When to Use Command Center

**Ideal for:**
- High-volume emergency departments (30+ patients/shift)
- Triage masters managing queue from central station
- Facilities with large monitors/workstations
- Urban hospitals with diverse, complex patient mix

**Not ideal for:**
- Mobile-first workflows (ambulance triage)
- Small clinics (under 10 patients at once)
- Bedside triage requiring portability
- Resource-limited settings (slow internet)

## Next Steps

1. **Prototype:** Build interactive mockup in Figma/React
2. **User Test:** Validate with actual triage nurses
3. **Measure:** Track time-to-triage in pilot
4. **Iterate:** Based on real-world feedback
