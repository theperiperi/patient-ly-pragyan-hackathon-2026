# UI Experiments for ABDM Triage System

## Overview

This directory contains research, concepts, and prototypes for building a **triage augmentation system** for healthcare workers. The system leverages the **ABDM (Ayushman Bharat Digital Mission)** local development kit to aggregate patient data from multiple sources and provide actionable insights for rapid triage decisions.

## Problem Statement

**Current Challenge:**
Triage masters in Indian hospitals waste significant time manually gathering patient information from fragmented sources (ambulance reports, previous hospital records, lab results, medication history). This delays critical triage decisions and can impact patient outcomes.

**Our Solution:**
An intelligent triage interface that:
- Automatically aggregates patient data from ABDM, ambulance systems, EMRs
- Presents complete medical context within 60-90 seconds
- Provides AI-powered triage suggestions based on historical patterns
- Works across desktop and mobile devices
- Augments (not replaces) human triage expertise

## Directory Structure

```
ui-experiments/
├── README.md                          # This file
├── research/
│   └── triage-systems-research.md     # Comprehensive research on existing systems
├── prototypes/
│   ├── CONCEPT_A_COMMAND_CENTER.md    # Desktop dashboard for queue management
│   ├── CONCEPT_B_PATIENT_FIRST.md     # Mobile-optimized bedside triage
│   ├── CONCEPT_C_TIMELINE_CENTRIC.md  # Timeline visualization for complex patients
│   ├── CONCEPT_D_HYBRID_SPLIT_VIEW.md # Split-screen queue + detail
│   └── CONCEPT_COMPARISON.md          # Side-by-side comparison & recommendations
└── assets/                            # (Future: Wireframes, mockups, icons)
```

## Research Summary

📖 **See:** `research/triage-systems-research.md`

**Key Findings:**
- **60-90 second rapid assessment** is the target time for triage (research-backed)
- **Color-coded priority systems** (RED-YELLOW-GREEN) are universally used
- **Mobile apps improved triage speed by 18+ minutes** vs paper (KatApp study)
- **Timeline visualization** enables 90-second patient history review
- **80% of digital triage happens on mobile devices**
- **AIIMS Triage Protocol (ATP)** is widely used in India (RED-YELLOW-GREEN)
- **No existing integration** between ATP and ABDM systems (opportunity!)

**Sources:** 56 academic papers, case studies, healthcare IT vendors, Indian healthcare institutions

## UI Concepts

We've developed **4 distinct UI concepts**, each optimized for different use cases:

### Concept A: Command Center
**Desktop dashboard for managing multiple patients simultaneously**

**Best for:** High-volume EDs (30-50+ patients/shift), triage masters at central workstation

**Key Features:**
- Grid-based queue with color-coded priority (RED, YELLOW, GREEN)
- Patient cards with vital signs and alerts at a glance
- Modal detail view for deep dive (60-90s assessment)
- Real-time dashboard updates

**Development:** 13 weeks | **See:** `prototypes/CONCEPT_A_COMMAND_CENTER.md`

---

### Concept B: Patient-First Mobile
**Mobile-optimized, offline-capable bedside triage**

**Best for:** Triage nurses moving between patients with tablet/phone, ambulance paramedics

**Key Features:**
- Touch-optimized with large tap targets (44px+)
- Swipe gestures for rapid navigation
- Offline-first with background sync
- Voice input for hands-free operation
- Battery-efficient for long shifts

**Development:** 18 weeks | **See:** `prototypes/CONCEPT_B_PATIENT_FIRST.md`

---

### Concept C: Timeline-Centric
**Timeline visualization showing complete patient health journey**

**Best for:** Complex patients with extensive history, chronic disease management, teaching hospitals

**Key Features:**
- Horizontal timeline showing 90 days of patient history
- Visual pattern recognition (trends, recurring issues, escalations)
- Multi-dimensional swim lanes (encounters, labs, meds, vitals)
- AI-powered insights based on timeline patterns
- Trend analysis charts

**Development:** 20 weeks | **See:** `prototypes/CONCEPT_C_TIMELINE_CENTRIC.md`

---

### Concept D: Hybrid Split-View
**Persistent split-screen: queue management + patient detail**

**Best for:** Busy EDs needing both queue awareness and patient depth, large monitor setups (27"+)

**Key Features:**
- 40% queue / 60% detail split (resizable)
- Comparison mode (view two patients side-by-side)
- Smart prefetch (zero-wait patient switching)
- Real-time collaboration (multi-user awareness)
- Flexible layout (collapse, resize, pop-out panels)

**Development:** 22 weeks | **See:** `prototypes/CONCEPT_D_HYBRID_SPLIT_VIEW.md`

---

## Comparison & Decision Guide

📊 **See:** `prototypes/CONCEPT_COMPARISON.md`

**Quick Decision Tree:**

1. **Mobile/bedside triage?** → Choose **Concept B**
2. **Desktop with large monitor?** → Choose **Concept A** or **D**
3. **Complex patients with long history?** → Choose **Concept C**
4. **Need both queue + detail?** → Choose **Concept D**
5. **Fastest to build?** → Choose **Concept A** (13 weeks)
6. **Most features?** → Choose **Concept D** (22 weeks)

**Hackathon Recommendation (2 weeks):**
Build a **Hybrid MVP** with simplified features from A + B + C:
- Basic queue dashboard (Concept A)
- Mobile-responsive (Concept B)
- Timeline panel (Concept C)
- AI insights
- Real ABDM integration

## ABDM Integration

All concepts integrate with the **ABDM Local Development Kit** (in parent directory):

**Core Workflow:**
```python
from abdm_client import ABDMClient

# 1. Patient identification (ABHA number or demographics)
client = ABDMClient(base_url="http://localhost:8090")

# 2. Discover patient across HIPs
discovery = await client.hip.discover_patient(
    abha_number="22-7225-4829-5255@sbx"
)

# 3. Request emergency consent (streamlined for triage)
consent = await client.hiu.request_consent(
    patient_abha="22-7225-4829-5255@sbx",
    purpose="CAREMGT",
    hi_types=["DiagnosticReport", "Prescription", "DischargeSummary"],
    date_range=(90_days_ago, today),
    emergency=True
)

# 4. Fetch health records from multiple HIPs
records = await client.hiu.fetch_health_information(consent.id)

# 5. Parse FHIR bundles for UI display
from fhir.resources.bundle import Bundle

for record in records:
    bundle = Bundle.parse_obj(record)
    # Extract: Conditions, Medications, Observations, Procedures, etc.
```

**Data Sources Integrated:**
- 🚑 **Ambulance:** Pre-hospital data (vitals in transit, interventions)
- 🏥 **ABDM HIPs:** Historical records from other hospitals (via FHIR)
- 🧪 **Lab Systems:** Recent test results
- 💊 **Pharmacy:** Current medications
- 📱 **Patient App:** (Future) Self-reported symptoms, wearable data

## Target User Persona

**Primary User: Triage Master**
- **Role:** Experienced nurse or physician responsible for initial patient assessment
- **Environment:** Emergency department of Indian hospital (public or private)
- **Daily Volume:** 30-50 patients per shift (busy urban ED)
- **Pain Points:**
  - Fragmented patient data across multiple systems
  - Time wasted manually gathering information (10-15 min per patient)
  - Incomplete medical history leads to suboptimal triage decisions
  - No access to previous hospital records (patient moved cities)
  - Ambulance reports on paper, not integrated digitally

**Workflow Goals:**
1. **Identify patient** (ABHA card scan or manual entry)
2. **Auto-fetch complete medical history** (< 3 seconds)
3. **Review at a glance** (60-90 seconds)
4. **Assign triage level** (ESI 1-5 or ATP RED/YELLOW/GREEN)
5. **Handoff to treating physician** with complete triage package

**Success Metric:** Complete triage in 60-90 seconds (down from current 10-15 minutes)

## Technical Stack (Recommended)

Based on research and concept designs:

### Frontend
```
Framework: Next.js (React 18+, TypeScript)
          OR React Native (for native mobile apps)

State: Zustand (lightweight) or Redux Toolkit (complex state)
Data Fetching: React Query (caching, prefetch, stale-while-revalidate)
UI Components: Shadcn/ui (Tailwind-based, accessible)
Charts: Recharts (vital trends, timeline viz)
Real-time: Socket.io or WebSocket
Forms: React Hook Form + Zod (validation)
Date: date-fns (lightweight date manipulation)
```

### Backend (Already Built!)
```
Services: FastAPI microservices (Gateway, Consent Manager, HIP, HIU)
Database: MongoDB (patients, consents, health records)
FHIR: fhir.resources library (Python FHIR R4)
Auth: JWT session tokens
SDK: abdm-client (Python SDK in ../sdk/python/)
```

### Deployment
```
Frontend: Vercel (Next.js) or Netlify
Backend: Docker Compose (already configured)
Database: MongoDB Atlas or self-hosted
Cache: Redis (for ABDM data caching)
```

## Development Roadmap

### Phase 1: Research & Design (DONE ✅)
- [x] Research existing triage systems
- [x] Design 4 UI concepts
- [x] Create comparison matrix
- [x] Define user personas

### Phase 2: Prototype (NEXT)
- [ ] Choose primary concept (A, B, C, or D)
- [ ] Build interactive mockup (Figma or code)
- [ ] User testing with triage nurses (5-10 users)
- [ ] Iterate based on feedback

### Phase 3: MVP Development (Hackathon or Production)
**Hackathon Track (2 weeks):**
- [ ] Simplified hybrid UI (A + B + C features)
- [ ] ABDM integration (discovery + fetch + parse)
- [ ] Mock data for demo (20-30 patient scenarios)
- [ ] AI risk scoring (simple ML model)
- [ ] Demo script preparation

**Production Track (13-22 weeks):**
- [ ] Full implementation of chosen concept
- [ ] ABDM production integration
- [ ] Real patient data (seeded from ABDM DevKit)
- [ ] AI model training (on real patient timelines)
- [ ] Security audit (patient data protection)
- [ ] Performance testing (handle 50+ concurrent patients)

### Phase 4: Testing & Validation
- [ ] Usability testing (System Usability Scale > 78)
- [ ] Clinical validation (accuracy of AI suggestions)
- [ ] Performance testing (< 2s dashboard load, < 500ms detail view)
- [ ] Security testing (ABDM compliance, data encryption)
- [ ] Pilot deployment (1-2 hospitals)

### Phase 5: Production Deployment
- [ ] Hospital integration (EMR, lab systems, pharmacy)
- [ ] Training materials for triage staff
- [ ] Rollout plan (staged deployment)
- [ ] Monitoring & analytics (triage time metrics)
- [ ] Continuous improvement (based on real-world usage)

## Success Metrics

**Primary Metrics:**
- ⏱ **Triage Time:** < 90 seconds (down from 10-15 minutes)
- ✅ **Triage Accuracy:** > 90% match physician assessment
- 📊 **System Usability:** SUS score > 78 (research benchmark)
- 🚀 **User Adoption:** > 80% triage staff prefer vs manual process

**Secondary Metrics:**
- ABDM data fetch speed: < 3 seconds
- Patient satisfaction: Reduced wait times
- Data completeness: > 85% patients have ABDM records
- Alert accuracy: < 10% false positives (avoid alert fatigue)

## Resources & References

**Research Document:**
- `research/triage-systems-research.md` (56 sources, 1100+ lines)

**Key Academic Sources:**
- Emergency Department triage systems (PMC, JMIR, BMC)
- Mobile triage applications (KatApp, Triagist)
- FHIR visualization tools (Trove Health, Open Health Hub)
- Indian healthcare context (AIIMS ATP, ABDM integration)

**Healthcare UI/UX:**
- Healthcare dashboard design best practices
- Clinical decision support system (CDSS) design
- Alert and notification design (avoid fatigue)
- Accessibility in healthcare (WCAG 2.1 AA)

**ABDM Resources:**
- ABDM Developer Portal: https://sandbox.abdm.gov.in/docs
- FHIR Implementation Guide (v6.5.0): Included in `fhir-profiles/`
- Sample FHIR bundles (277 examples): In `fhir-samples/`

## Next Steps

1. **Review all concept documents** (`prototypes/CONCEPT_*.md`)
2. **Read comparison matrix** (`prototypes/CONCEPT_COMPARISON.md`)
3. **Decide on primary concept** (or hybrid approach)
4. **If Hackathon:**
   - Build hybrid MVP (2 weeks)
   - Focus on demo wow factor
   - Real ABDM integration
5. **If Production:**
   - Start with Concept A (13 weeks)
   - Add mobile later (Concept B)
   - Iterate based on user feedback

## Questions?

**For Hackathon:**
- Which features are most impressive to judges? → ABDM integration + AI insights + timeline viz
- Can we build in 2 weeks? → Yes, simplified hybrid MVP
- What's the winning demo? → Show real FHIR data aggregation, timeline, AI predictions

**For Production:**
- Which concept is safest bet? → Concept A (proven workflow, moderate complexity)
- Can we do it all? → Yes, but phase it (A → B → C → D over 42 weeks)
- What's the ROI? → 10-15 min → 90s per patient = 90% time savings

## License

MIT License (same as ABDM Local Development Kit)

---

**Ready to build the future of healthcare triage in India! 🏥🇮🇳**

Let's make triage masters' lives easier, one patient at a time. 💪
