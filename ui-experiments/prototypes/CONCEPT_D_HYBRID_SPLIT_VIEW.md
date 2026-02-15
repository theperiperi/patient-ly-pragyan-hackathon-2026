# UI Concept D: "Hybrid Split-View"

## Overview
Combines queue management dashboard (Concept A) with patient-first detail view (Concepts B/C) in a persistent split-screen layout. Best of both worlds: monitor multiple patients while maintaining deep context for active triage.

**Target User:** Triage master who needs to juggle multiple critical patients while conducting detailed assessments

**Key Principle:** "Parallel Processing" - Never lose sight of the queue while diving deep into individual cases

## Core Design Philosophy

- **Persistent split-screen** - Queue always visible (left), detail always accessible (right)
- **Contextual switching** - Click any patient, right panel updates instantly
- **Comparison mode** - View two patients side-by-side when needed
- **Flexible layout** - Resize, collapse, or pop-out panels as needed
- **Unified actions** - Triage decisions visible in both panels simultaneously

## Wireframe Layout (Desktop - Primary Use Case)

### Default Layout: 40% Queue / 60% Detail

```
┌────────────────────────────────────────────────────────────────────────────┐
│ HYBRID TRIAGE WORKSTATION              [Hospital Name]  [User]  [Settings] │
├───────────────────────┬────────────────────────────────────────────────────┤
│                       │                                                     │
│ QUEUE (28 patients)   │ ACTIVE PATIENT                                     │
│ [Search] [Filter ⏱]  │ Rajesh Kumar, 45M | ABHA: **-5255                  │
│                       │ 🔴 CRITICAL - Chest Pain | ⏱ 3 min | 🚑           │
│ ┏━━━━━━━━━━━━━━━━━━┓│ ┌────────────────────────────────────────────────┐ │
│ ┃ 🔴 CRITICAL (3)  ┃│ │ CURRENT STATUS         DATA SOURCES             │ │
│ ┗━━━━━━━━━━━━━━━━━━┛│ ├────────────────────────────────────────────────┤ │
│                       │ │ Vitals (Live):         ✓ Ambulance (3m ago)    │ │
│ ┌─────────────────┐  │ │ BP: 180/110 ⚠         ✓ Apollo (2d, ABDM)      │ │
│ │ ⚫ Rajesh K., 45M│  │ │ HR: 125 ⚠             ✓ Labs (10d, ABDM)       │ │
│ │ ⏱ 3m 🚑 Chest  │  │ │ SpO2: 94% ⚠           ✓ Pharmacy (Local)        │ │
│ │ BP↑ HR↑ SpO2↓   │  │ │ RR: 22/min ⚠                                   │ │
│ └─────────────────┘  │ │                        [Fetch more HIPs]        │ │
│ ┌─────────────────┐  │ └────────────────────────────────────────────────┘ │
│ │ Priya S., 28F   │  │                                                     │
│ │ ⏱ 7m 🚗 Abd pain│  │ ⚠ CRITICAL ALERTS                                  │
│ │ BP↓ Pregnant    │  │ • Previous MI 2 years ago (Apollo ABDM record)     │
│ └─────────────────┘  │ • Diabetic on insulin (Current)                    │
│ ┌─────────────────┐  │ • ALLERGY: Penicillin - Anaphylaxis risk          │
│ │ Anil P., 62M    │  │                                                     │
│ │ ⏱ 12m 🚑 AMS    │  │ ┌──────────────┬───────────────┬─────────────────┐ │
│ └─────────────────┘  │ │ 💊 MEDS (5)  │ 📋 CONDITIONS │ 📊 RECENT LABS  │ │
│                       │ ├──────────────┴───────────────┴─────────────────┤ │
│ ┏━━━━━━━━━━━━━━━━━━┓│ │ • Metformin 500mg BD    Type 2 DM               │ │
│ ┃ 🟡 URGENT (12)   ┃│ │ • Aspirin 75mg OD       Hypertension            │ │
│ ┗━━━━━━━━━━━━━━━━━━┛│ │ • Atorvastatin 20mg OD  CAD (s/p MI)            │ │
│                       │ │ • Metoprolol 25mg BD                            │ │
│ ┌─────────────────┐  │ │ • Lisinopril 10mg OD    Last: 10 days ago       │ │
│ │ Meena S., 35F   │  │ │                         Cholesterol: 245 ⚠ HIGH │ │
│ │ ⏱ 18m Fever,rash│  │ │ Source: Apollo Hospital HbA1c: 7.2% Controlled  │ │
│ └─────────────────┘  │ └─────────────────────────────────────────────────┘ │
│ ┌─────────────────┐  │                                                     │
│ │ Arjun D., 52M   │  │ 📅 TIMELINE (Last 30 Days)          [Expand to 90d]│
│ │ ⏱ 22m Knee pain │  │ ├─ TODAY 10:30 - 🚑 Ambulance: Chest pain, ECG ST↑│
│ └─────────────────┘  │ ├─ 2d ago - 🏥 Apollo: Cardio F/U, stable          │
│ [+10 more...]        │ ├─ 10d ago - 🧪 Labs: Lipid panel abnormal         │
│                       │ └─ [View complete history]                         │
│ ┏━━━━━━━━━━━━━━━━━━┓│                                                     │
│ ┃ 🟢 MINOR (8)     ┃│ 🤖 AI TRIAGE ASSISTANT                             │
│ ┗━━━━━━━━━━━━━━━━━━┛│ ┌─────────────────────────────────────────────────┐│
│                       │ │ LIKELY: Acute MI (STEMI) - 92% confidence       ││
│ [Show all...]         │ │                                                  ││
│                       │ │ RECOMMENDED:                                     ││
│ ┏━━━━━━━━━━━━━━━━━━┓│ │ 1. Activate Code STEMI                           ││
│ ┃ 🔵 IN TX (5)     ┃│ │ 2. Notify cath lab                               ││
│ ┗━━━━━━━━━━━━━━━━━━┛│ │ 3. STAT troponin, repeat ECG                     ││
│                       │ │ 4. Cardiology consult < 15 min                   ││
│ [Show all...]         │ │ 5. Critical care bay assignment                  ││
│                       │ └─────────────────────────────────────────────────┘│
│                       │                                                     │
│ ━━━━━━━━━━━━━━━━━━━━│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ DEPARTMENT STATUS     │ TRIAGE ACTIONS (for Rajesh Kumar)                  │
│ Total: 28/45          │ ┌────────┬────────┬────────┬────────┬────────────┐│
│ RED: 3 | YELLOW: 12   │ │ ESI    │ ASSIGN │ CALL   │ ORDER  │ COMPLETE   ││
│ GREEN: 8 | BLUE: 5    │ │ LEVEL  │ BAY    │ CARDIO │ STAT   │ & HANDOFF  ││
│ Avg Wait: 15 min      │ │ [1-5]  │ [Resus]│ [Now]  │ [Labs] │ [Next Pt]  ││
│                       │ └────────┴────────┴────────┴────────┴────────────┘│
└───────────────────────┴────────────────────────────────────────────────────┘
```

### Alternative Layout: Comparison Mode (Two Patients Side-by-Side)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ COMPARISON MODE: Rajesh Kumar vs Priya Sharma             [Exit Compare] [X]│
├───────────────────────────────────┬────────────────────────────────────────┤
│ Rajesh Kumar, 45M                 │ Priya Sharma, 28F                      │
│ 🔴 CRITICAL - Chest Pain          │ 🔴 CRITICAL - Abdominal Pain           │
│ ⏱ 3 min | 🚑 Ambulance            │ ⏱ 7 min | 🚗 Walk-in                  │
├───────────────────────────────────┼────────────────────────────────────────┤
│ VITALS                            │ VITALS                                 │
│ BP: 180/110 ⚠ HIGH               │ BP: 90/60 ⚠ LOW (hypotensive)         │
│ HR: 125 ⚠ HIGH                   │ HR: 110 ⚠ ELEVATED                    │
│ SpO2: 94% ⚠ LOW                  │ SpO2: 98% ✓ Normal                    │
│ Temp: 98.6°F ✓                   │ Temp: 102°F ⚠ FEVER                   │
│ RR: 22/min ⚠                     │ RR: 18/min ✓                          │
├───────────────────────────────────┼────────────────────────────────────────┤
│ ALERTS                            │ ALERTS                                 │
│ • Previous MI (2 years ago)       │ • PREGNANT (12 weeks) ⚠⚠⚠            │
│ • Diabetic (insulin)              │ • No known medical history             │
│ • Allergy: Penicillin             │ • No known allergies                   │
├───────────────────────────────────┼────────────────────────────────────────┤
│ CURRENT MEDICATIONS (5)           │ CURRENT MEDICATIONS (0)                │
│ Cardiac + diabetes meds           │ None on record                         │
├───────────────────────────────────┼────────────────────────────────────────┤
│ AI ASSESSMENT                     │ AI ASSESSMENT                          │
│ STEMI - 92% confidence            │ Ectopic pregnancy? - 65% confidence    │
│ Recommend: Code STEMI             │ Appendicitis? - 45% confidence         │
│               Cath lab            │ Recommend: OB/GYN STAT consult         │
│               STAT ECG/Troponin   │            Ultrasound STAT             │
│                                   │            Surgical consult if needed  │
├───────────────────────────────────┼────────────────────────────────────────┤
│ PRIORITY RECOMMENDATION           │ PRIORITY RECOMMENDATION                │
│ ⚠ HIGHER PRIORITY                │ ⚠ EQUAL OR HIGHER (pregnancy risk)    │
│   (acute cardiac, known history)  │   (maternal + fetal risk)              │
│                                   │                                        │
│ Suggested: Both critical, handle  │ Suggested: May need to triage both     │
│ in parallel if possible           │ simultaneously with 2 teams            │
└───────────────────────────────────┴────────────────────────────────────────┘
│ [TRIAGE RAJESH: ESI 1, Resus Bay 1] [TRIAGE PRIYA: ESI 1, OB Bay]        │
└────────────────────────────────────────────────────────────────────────────┘
```

### Collapsed Queue Mode (When Focused on Single Patient)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ☰ (collapsed queue)   │ ACTIVE: Rajesh Kumar, 45M                          │
│                       │ 🔴 CRITICAL - Chest Pain                           │
│ 🔴 3                  │                                                     │
│ 🟡 12                 │ [Full patient detail occupies entire right side... │
│ 🟢 8                  │  with timeline, vitals, meds, AI insights, etc.]   │
│ 🔵 5                  │                                                     │
│                       │                                                     │
│ [◄ Expand]           │                                                     │
│                       │                                                     │
│ ━━━━━━━━━━━━━━━━━━━━│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Prev | Next          │ [Actions: ESI, Assign Bay, Call, Order, Complete]  │
└───────────────────────┴────────────────────────────────────────────────────┘
```

## Key Features

### 1. Persistent Queue Awareness

**Never Lose Context:**
- Queue always visible on left (or collapsed to slim sidebar)
- Real-time updates: New patients appear, wait times update
- Color-coded counts at a glance (RED: 3, YELLOW: 12, etc.)
- Can click any patient in queue → Right panel updates instantly

**Visual Priority:**
```
Queue Visual Design:

ACTIVE PATIENT (currently viewing):
┌───────────────────────────┐
│ ⚫ Rajesh Kumar, 45M       │ ← Dark circle = selected
│ ⏱ 3m 🚑 Chest pain        │ ← Highlighted background
│ BP↑ HR↑ SpO2↓             │
└───────────────────────────┘

INACTIVE PATIENTS:
┌───────────────────────────┐
│ ○ Priya Sharma, 28F       │ ← Empty circle = not selected
│ ⏱ 7m 🚗 Abdominal pain    │ ← Normal background
│ BP↓ Pregnant              │
└───────────────────────────┘
```

### 2. Flexible Layout Options

**Resize Panels:**
- Drag divider left/right to adjust split ratio
- Common ratios: 30/70, 40/60, 50/50
- User preference saved per login

**Collapse Modes:**
- **Queue collapsed:** Slim sidebar with counts only (95% screen to detail)
- **Detail collapsed:** Full queue view (list mode)
- **Both visible:** Default split-screen

**Pop-out Panels (Multi-Monitor Support):**
- Pop-out patient detail to second monitor
- Pop-out queue to second monitor
- Allows even more screen real estate

### 3. Comparison Mode

**When to Compare:**
- Multiple critical patients (need to decide priority)
- Similar presentations (differential diagnosis)
- Family members (multiple patients from same event)
- Quality assurance (compare triage decisions)

**How to Activate:**
```
METHOD 1: Drag patient card onto detail panel
  → Enters comparison mode

METHOD 2: Right-click patient → "Compare with current"

METHOD 3: Select multiple (Ctrl+Click) → "Compare Selected"

METHOD 4: Keyboard: Select patient, press 'C' key
```

**Comparison Features:**
- Side-by-side vitals (easy to spot differences)
- Parallel AI recommendations
- Priority suggestion (which to triage first)
- Dual action bars (can triage both simultaneously)

### 4. Unified Actions Across Panels

**Action Visibility:**
```
When you assign ESI level or bay on RIGHT panel,
LEFT panel queue card updates in real-time:

BEFORE TRIAGE:
┌───────────────────────────┐
│ ⚫ Rajesh Kumar, 45M       │
│ ⏱ 3m 🚑 Chest pain        │
│ BP↑ HR↑ SpO2↓             │
│ [Not yet triaged]         │
└───────────────────────────┘

AFTER TRIAGE:
┌───────────────────────────┐
│ ✓ Rajesh Kumar, 45M       │ ← Green checkmark
│ ESI 1 | Resus Bay 1       │ ← Shows triage decision
│ 🏥 Dr. Shah (Cardiology)  │ ← Assigned physician
│ [Triaged 30s ago]         │
└───────────────────────────┘
```

**Batch Actions:**
```
Select multiple patients in queue (Ctrl+Click):
→ [Assign all to ESI 3]
→ [Call waiting room for all]
→ [Print all wristbands]
→ [Send all to X-ray queue]
```

### 5. Quick Navigation

**Keyboard Shortcuts:**
```
Queue Navigation:
↑ / ↓  : Previous/Next patient in queue
1-5    : Jump to ESI level (1=critical, 5=non-urgent)
R      : Jump to RED patients
Y      : Jump to YELLOW patients
G      : Jump to GREEN patients

Patient Actions:
E      : Assign ESI level (popup)
B      : Assign to bay (popup)
C      : Call specialist (popup)
O      : Order tests (popup)
Enter  : Complete triage & move to next
Esc    : Cancel/Close current panel

Layout:
[      : Collapse queue
]      : Collapse detail
\      : Toggle comparison mode
Tab    : Switch focus (queue ↔ detail)
```

**Mouse Shortcuts:**
```
Double-click patient: Load in detail panel
Right-click patient: Context menu (assign, compare, defer, etc.)
Drag patient: Reorder priority or compare
Scroll queue: Infinite scroll through all patients
Hover patient: Preview tooltip with key info
```

### 6. ABDM Integration (Optimized for Split-View)

**Parallel Data Fetching:**
```python
# While viewing Patient A in detail panel,
# pre-fetch data for next patients in queue:

async def smart_prefetch_strategy():
    """
    Pre-fetch ABDM data for likely-next patients
    to reduce wait time when switching
    """

    # Get current active patient
    current = get_active_patient()

    # Predict next patients (based on queue order + priority)
    next_patients = predict_next_triage_targets(queue, n=3)

    # Pre-fetch in background (non-blocking)
    await asyncio.gather(*[
        prefetch_abdm_data(patient.abha)
        for patient in next_patients
    ])

    # Cache results for instant display when selected

async def prefetch_abdm_data(abha_number):
    """
    Background fetch and cache
    """
    try:
        data = await fetch_patient_abdm_data(abha_number)
        cache.set(f"abdm:{abha_number}", data, ttl=300)  # 5 min cache

        # Update queue card with indicator
        update_queue_card(abha_number, {"abdm_ready": True})
    except Exception as e:
        log_error(f"Prefetch failed for {abha_number}: {e}")

# Visual indicator in queue:
┌───────────────────────────┐
│ Priya Sharma, 28F         │
│ ✓ ABDM data ready         │ ← Green checkmark = cached
│ ⏱ 7m 🚗 Abdominal pain    │
└───────────────────────────┘

┌───────────────────────────┐
│ Anil Patel, 62M           │
│ ↻ Loading ABDM data...    │ ← Spinner = fetching
│ ⏱ 12m 🚑 AMS              │
└───────────────────────────┘
```

### 7. Smart Queue Management

**Auto-Prioritization:**
```javascript
// AI-powered queue reordering suggestions

function suggest_queue_reordering(queue, context) {
    """
    Analyze queue and suggest priority changes
    based on:
    - Wait time (patients waiting too long)
    - Vital signs (deteriorating patients)
    - AI risk scores (predicted bad outcomes)
    - Resource availability (open bays/specialists)
    """

    const suggestions = []

    for (const patient of queue) {
        // Deterioration detection
        if (patient.vitals_trend === 'worsening') {
            suggestions.push({
                patient: patient.id,
                action: 'escalate',
                reason: 'Vitals deteriorating',
                old_esi: patient.esi,
                new_esi: patient.esi - 1  // More urgent
            })
        }

        // Wait time alerts
        if (patient.wait_time > get_max_wait(patient.esi)) {
            suggestions.push({
                patient: patient.id,
                action: 'alert',
                reason: `Exceeded max wait for ESI ${patient.esi}`,
                wait_time: patient.wait_time,
                max_wait: get_max_wait(patient.esi)
            })
        }

        // AI high-risk flagging
        if (patient.ai_risk_score > 0.8 && patient.esi > 2) {
            suggestions.push({
                patient: patient.id,
                action: 'escalate',
                reason: 'AI predicts high risk',
                ai_score: patient.ai_risk_score,
                suggested_esi: 2
            })
        }
    }

    return suggestions
}

// UI Presentation:
┌───────────────────────────────────┐
│ ⚠ QUEUE RECOMMENDATIONS (3)       │
│                                    │
│ 1. Escalate Meena Singh to ESI 2  │
│    Reason: Wait time 35m (max 30m) │
│    [Apply] [Dismiss]               │
│                                    │
│ 2. Re-assess Arjun Das            │
│    Reason: BP increased 140→165    │
│    [View Patient] [Dismiss]        │
│                                    │
│ 3. Priority: Lakshmi Reddy         │
│    Reason: AI risk score 0.87      │
│    [Escalate to ESI 2] [Dismiss]   │
└───────────────────────────────────┘
```

### 8. Real-Time Collaboration

**Multi-User Awareness:**
```
When colleague opens same patient:

┌───────────────────────────┐
│ 👁️ Dr. Patel viewing      │ ← Eye icon = someone else looking
│ Rajesh Kumar, 45M         │
│ ⏱ 3m 🚑 Chest pain        │
└───────────────────────────┘

When colleague triages patient while you're viewing:
→ Toast notification: "Dr. Patel triaged this patient to ESI 1, Resus Bay 1"
→ Option: [View their notes] [Dismiss]
```

**Lock Prevention:**
```
// Optimistic locking to prevent conflicts

If you start triaging patient:
→ Soft lock applied (others can view but warned)
→ Timer: 5 minutes (auto-release if idle)
→ Others see: "⏱ Reserved by Dr. Kumar (3 min remaining)"

If someone else tries to triage same patient:
→ Warning: "Dr. Kumar is currently triaging this patient"
→ Options:
  - [Wait and notify me when done]
  - [Take over (notify Dr. Kumar)]
  - [View read-only and collaborate]
```

## Workflow Example (60-Second Triage)

**Scenario: Triage Rajesh Kumar (chest pain)**

```
0-5s:  Patient appears in RED queue (ambulance pre-arrival notification)
5-10s: ABDM data pre-fetched (done before triage master even clicks)
10s:   Click patient in queue → Detail panel populates instantly
15s:   Scan vitals in detail panel (BP↑, HR↑, SpO2↓ = bad)
20s:   Read critical alerts (Previous MI, diabetic, penicillin allergy)
30s:   Review ambulance ECG (ST elevation = STEMI confirmed)
40s:   Check AI recommendation (Code STEMI, cath lab, 92% confidence)
50s:   Click [ESI Level: 1], [Assign: Resus Bay 1], [Call: Cardiology]
55s:   Click [Activate Code STEMI] (auto-orders STAT labs/ECG)
60s:   Click [Complete Triage] → Patient handed off to treating team

Queue card updates:
✓ Rajesh Kumar, 45M
ESI 1 | Resus Bay 1
🏥 Dr. Shah (Cardiology)
[Triaged - just now]

Next patient auto-selected:
⚫ Priya Sharma, 28F (next critical)
Detail panel updates with her data (already cached)

Total time: 60 seconds
```

## Technology Stack

```javascript
// Frontend: React with TypeScript

Layout Management:
- react-grid-layout (for resizable panels)
- react-split-pane (for draggable divider)
- react-window (virtual scrolling for long queues)

State Management:
- Zustand (lightweight, perfect for split state)
- Real-time sync with WebSocket

Data Fetching:
- React Query (cache, prefetch, stale-while-revalidate)
- Optimistic updates for fast UI

UI Components:
- Shadcn/ui (accessible, customizable)
- Framer Motion (smooth panel transitions)

// Backend: FastAPI + WebSocket

Real-time Updates:
- Server-Sent Events (SSE) or WebSocket for queue updates
- Push new patients, vital changes, triage completions

Caching Strategy:
- Redis for ABDM data cache (5-min TTL)
- Pre-fetch next N patients in queue
- Invalidate on patient update

// Performance Targets:
- Panel switch: < 100ms (with cache hit)
- Queue update latency: < 500ms (real-time)
- Detail panel load: < 300ms (cached data)
- Comparison mode: < 200ms (render two patients)
```

## Responsive Design

**Tablet (iPad Pro Landscape):**
- Default split-view works well
- Touch targets enlarged to 44px+
- Swipe gestures for panel navigation

**Tablet (iPad Portrait):**
- Auto-collapse to single panel at a time
- Swipe left/right to switch queue ↔ detail
- Bottom sheet for actions

**Desktop (Large Monitors 27"+):**
- Default 40/60 split
- Consider triple-pane: Queue | Detail | Timeline
- Multi-monitor support (pop-out panels)

## Strengths of This Concept

✅ **Best of Both Worlds:** Queue awareness + deep patient context
✅ **Minimal Context Switching:** Everything visible, no navigation
✅ **Comparison Capability:** Side-by-side critical patients
✅ **Scalable:** Works for 10 or 100 patients
✅ **Flexible:** Adapt layout to task (collapse, resize, pop-out)
✅ **Real-Time Collaboration:** Multi-user awareness
✅ **Smart Prefetch:** Zero-wait patient switching (with cache)

## Limitations

❌ **Complex UI:** Steeper learning curve than single-panel views
❌ **Screen Size Dependent:** Requires large display (min 1920px wide)
❌ **Information Overload Risk:** Too much visible at once (can distract)
❌ **Not Mobile-Friendly:** Split-view doesn't work on phones

## When to Use Hybrid Split-View

**Ideal for:**
- Busy emergency departments (30-50 patients/shift)
- Triage masters with large monitors (24"+ displays)
- Complex patient mix (many critical + urgent simultaneously)
- Multi-tasking workflows (triaging while monitoring queue)
- Teaching environments (compare patients, show patterns)
- Multi-user triage teams (collaboration features)

**Not ideal for:**
- Mobile/tablet-only workflows
- Small screens (< 1920px width)
- Simple triage (few patients, straightforward cases)
- Single-patient-at-a-time workflows

## User Testing Metrics

**Success Criteria:**
- Triage speed: < 90 seconds (match other concepts)
- Queue awareness: > 90% detect new critical patients within 10s
- Panel navigation: < 2 seconds to switch patients
- User preference: > 75% prefer split-view vs single-panel
- Multi-tasking: Ability to monitor 3+ critical patients simultaneously

## Accessibility

**Keyboard-First Design:**
- All functions accessible via keyboard
- Clear focus indicators in both panels
- Shortcuts for common actions

**Screen Reader Support:**
- Announce queue changes ("New critical patient: Rajesh Kumar")
- Announce active panel ("Now viewing patient detail")
- ARIA live regions for real-time updates

**Color & Contrast:**
- WCAG 2.1 AA compliant
- Color-blind safe palette (not just red/green)
- High contrast mode option

## Next Steps

1. **Interactive prototype** (Figma or React)
2. **User testing** with triage masters (observe panel usage)
3. **Performance testing** (measure panel switch speed with real data)
4. **A/B test** vs single-panel concepts
5. **Iterate** based on feedback (adjust default split ratio, prefetch strategy, etc.)
