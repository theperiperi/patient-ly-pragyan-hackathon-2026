# UI Concept B: "Patient-First Mobile"

## Overview
Mobile-optimized, card-based interface designed for bedside triage and portability. Inspired by KatApp research showing 18+ minute speed improvement with mobile apps and 80% of digital triage happening on mobile devices.

**Target User:** Triage nurse moving between waiting area and triage rooms, using tablet or large phone

**Key Principle:** "At Hand" - One or two touches for any action, works offline

## Core Design Philosophy

- **Mobile-first, touch-optimized** with large tap targets (44x44px minimum)
- **Swipe-based navigation** for rapid patient review
- **Offline-capable** with sync when connected
- **Simplified data entry** with smart defaults and voice input
- **Progressive enhancement** from phone → tablet → desktop

## Wireframe Layout (Portrait Phone)

### Main View: Queue List
```
┌─────────────────────────────────────┐
│  ☰  TRIAGE QUEUE      [🔔2]  [User] │
├─────────────────────────────────────┤
│ Today: 28 patients | 15 min avg wait│
│                                      │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ 🔴 CRITICAL - 3 PATIENTS        ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ 🔴 Rajesh Kumar, 45M   ⏱ 3min │  │
│ │ ABHA: **-5255  🚑 Ambulance    │  │
│ │                                 │  │
│ │ Chest pain, SOB                 │  │
│ │ BP 180/110 | HR 125 | SpO2 94%│  │
│ │                                 │  │
│ │ ⚠ Cardiac Hx  ⚠ Allergy: PCN   │  │
│ │ ────────────────────────────── │  │
│ │    [TRIAGE NOW]    [VIEW ALL]  │  │
│ └────────────────────────────────┘  │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ 🔴 Priya Sharma, 28F   ⏱ 7min │  │
│ │ ABHA: **-7891  🚗 Walk-in      │  │
│ │                                 │  │
│ │ Severe abdominal pain, vomiting │  │
│ │ BP 90/60 | HR 110 | Temp 102°F│  │
│ │                                 │  │
│ │ ⚠ Pregnant (12 weeks)           │  │
│ │ ────────────────────────────── │  │
│ │    [TRIAGE NOW]    [VIEW ALL]  │  │
│ └────────────────────────────────┘  │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ 🔴 Anil Patel, 62M    ⏱ 12min │  │
│ │ [Tap to expand...]              │  │
│ └────────────────────────────────┘  │
│                                      │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ 🟡 URGENT - 12 PATIENTS         ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ 🟡 Meena Singh, 35F   ⏱ 18min │  │
│ │ Fever 3 days, rash              │  │
│ │ [Tap for details...]            │  │
│ └────────────────────────────────┘  │
│                                      │
│ [Show 11 more...]                    │
│                                      │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ 🟢 MINOR - 8 PATIENTS           ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                      │
│ [Show all...]                        │
│                                      │
│                                      │
├─────────────────────────────────────┤
│ [➕ NEW]  [🔍 SEARCH]  [📊 STATS]   │
└─────────────────────────────────────┘
```

### Patient Detail View (Full Screen)
Swipe up from "[TRIAGE NOW]" or tap "[VIEW ALL]":

```
┌─────────────────────────────────────┐
│ ←                          [Done] [⋮]│
├─────────────────────────────────────┤
│ 🔴 CRITICAL                          │
│                                      │
│ Rajesh Kumar, 45M                    │
│ ABHA: 22-7225-4829-5255              │
│ Mobile: +91-9876543210               │
│                                      │
│ Arrived: 3 min ago via 🚑 Ambulance │
│ Location: Waiting Bay 2              │
├─────────────────────────────────────┤
│                                      │
│ CHIEF COMPLAINT                      │
│ ┌──────────────────────────────────┐│
│ │ Chest pain radiating to left arm ││
│ │ Shortness of breath              ││
│ │ Onset: 30 min ago                ││
│ │ [🎤 Add voice note]              ││
│ └──────────────────────────────────┘│
│                                      │
│ VITAL SIGNS                   [Live]│
│ ┌──────────────────────────────────┐│
│ │ 🫀 Blood Pressure                ││
│ │    180/110 mmHg ⚠ CRITICAL      ││
│ │    Last: 2 min ago              ││
│ │                                  ││
│ │ 💓 Heart Rate                    ││
│ │    125 bpm ⚠ HIGH               ││
│ │                                  ││
│ │ 🫁 SpO2                          ││
│ │    94% ⚠ LOW                    ││
│ │                                  ││
│ │ 🌡️ Temperature                   ││
│ │    98.6°F ✓ Normal              ││
│ │                                  ││
│ │ 🫁 Respiratory Rate              ││
│ │    22/min ⚠ ELEVATED            ││
│ │                                  ││
│ │ [📊 View Trends]                ││
│ └──────────────────────────────────┘│
│                                      │
│ ⚠ CRITICAL ALERTS                   │
│ ┌──────────────────────────────────┐│
│ │ • Previous MI 2 years ago        ││
│ │ • Diabetic on insulin            ││
│ │ • ALLERGY: Penicillin            ││
│ │   (Anaphylaxis risk)             ││
│ └──────────────────────────────────┘│
│                                      │
│ 💊 CURRENT MEDICATIONS         [ABDM]│
│ ┌──────────────────────────────────┐│
│ │ • Metformin 500mg BD             ││
│ │ • Aspirin 75mg OD                ││
│ │ • Atorvastatin 20mg OD           ││
│ │ • Metoprolol 25mg BD             ││
│ │ • Lisinopril 10mg OD             ││
│ │                                  ││
│ │ Source: Apollo Hospital          ││
│ │ Updated: 2 days ago              ││
│ │ [View full history]              ││
│ └──────────────────────────────────┘│
│                                      │
│ 📋 RECENT HISTORY          [Timeline]│
│ ┌──────────────────────────────────┐│
│ │ ▸ 3 min ago - Ambulance Report   ││
│ │   ECG: ST elevation, Aspirin given│││
│ │                                  ││
│ │ ▸ 2 days ago - Apollo Hospital   ││
│ │   Cardiology follow-up, stable   ││
│ │                                  ││
│ │ ▸ 3 days ago - Lab Results       ││
│ │   Cholesterol high, HbA1c 7.2%   ││
│ │                                  ││
│ │ [View complete EMR (2 years)]    ││
│ └──────────────────────────────────┘│
│                                      │
│ 📊 DATA SOURCES                      │
│ ┌──────────────────────────────────┐│
│ │ ✓ Ambulance pre-hospital data    ││
│ │ ✓ ABDM (Apollo Hospital)         ││
│ │ ✓ Lab results via ABDM           ││
│ │ ✓ Pharmacy database              ││
│ │ ⚠ No wearable data available     ││
│ │                                  ││
│ │ [Request additional HIPs]        ││
│ └──────────────────────────────────┘│
│                                      │
│ [Scroll for actions ↓]              │
│                                      │
└─────────────────────────────────────┘
```

### Action Panel (Bottom Sheet, Swipe Up)
```
┌─────────────────────────────────────┐
│              ━━━━                    │
│                                      │
│ TRIAGE ACTIONS                       │
│                                      │
│ ┌──────────────────────────────────┐│
│ │ ASSIGN TRIAGE LEVEL              ││
│ │                                  ││
│ │  1️⃣   2️⃣   3️⃣   4️⃣   5️⃣      ││
│ │ Critical  Urgent  Moderate  Low ││
│ │                                  ││
│ │ Selected: 1 (Critical)           ││
│ └──────────────────────────────────┘│
│                                      │
│ ┌──────────────────────────────────┐│
│ │ ASSIGN TO                        ││
│ │                                  ││
│ │ [🛏️ Resus Bay 1]                ││
│ │ [🛏️ Trauma Bay 2]                ││
│ │ [🛏️ Critical Care Bay 3]         ││
│ │                                  ││
│ │ [Select other...]                ││
│ └──────────────────────────────────┘│
│                                      │
│ ┌──────────────────────────────────┐│
│ │ NOTIFY TEAM                      ││
│ │                                  ││
│ │ [📞 Call Cardiology Resident]    ││
│ │ [🔔 Alert Cardiologist]          ││
│ │ [🚨 Code STEMI]                  ││
│ └──────────────────────────────────┘│
│                                      │
│ ┌──────────────────────────────────┐│
│ │ ORDER TESTS (STAT)               ││
│ │                                  ││
│ │ ☑ ECG (12-lead)                  ││
│ │ ☑ Troponin                       ││
│ │ ☑ CBC, BMP                       ││
│ │ ☑ Chest X-Ray                    ││
│ │ ☐ D-Dimer                        ││
│ │                                  ││
│ │ [Submit orders]                  ││
│ └──────────────────────────────────┘│
│                                      │
│ ┌──────────────────────────────────┐│
│ │ QUICK NOTES                      ││
│ │                                  ││
│ │ [Type or dictate...]             ││
│ │ [🎤 Voice note]                  ││
│ └──────────────────────────────────┘│
│                                      │
│ ┌──────────────────────────────────┐│
│ │     [COMPLETE TRIAGE]            ││
│ │     [Save as Draft]              ││
│ └──────────────────────────────────┘│
│                                      │
└─────────────────────────────────────┘
```

### Tablet Landscape Mode (iPad Pro)
```
┌──────────────────────────────────────────────────────────────────────┐
│  ☰  TRIAGE                    [Search] [🔔 2]  [User]  [Sync ✓]      │
├──────────────────────┬───────────────────────────────────────────────┤
│                      │                                                │
│ QUEUE                │ PATIENT DETAIL                                 │
│ 28 Patients          │                                                │
│                      │ 🔴 CRITICAL                                    │
│ 🔴 CRITICAL (3)      │                                                │
│                      │ Rajesh Kumar, 45M                              │
│ ┌──────────────────┐│ ABHA: 22-7225-4829-5255                        │
│ │ 🔴 Rajesh K., 45M││                                                │
│ │ ⏱ 3min  🚑       ││ ┌────────────────┬────────────────────────────┐│
│ │ Chest pain       ││ │ VITALS         │ ALERTS                     ││
│ │ BP↑ HR↑ SpO2↓   ││ │                │ • Previous MI              ││
│ └──────────────────┘│ │ BP: 180/110 ⚠ │ • Diabetic                 ││
│ ┌──────────────────┐│ │ HR: 125 ⚠     │ • Allergy: Penicillin      ││
│ │ 🔴 Priya S., 28F ││ │ SpO2: 94% ⚠   │                            ││
│ │ ⏱ 7min  🚗       ││ │ Temp: 98.6°F  │ CURRENT MEDS               ││
│ │ Abdominal pain   ││ │ RR: 22/min ⚠  │ • Metformin 500mg BD       ││
│ └──────────────────┘│ │                │ • Aspirin 75mg OD          ││
│ ┌──────────────────┐│ │ [View Trends]  │ • Atorvastatin 20mg OD     ││
│ │ 🔴 Anil P., 62M  ││ └────────────────┴────────────────────────────┘│
│ │ ⏱ 12min 🚑       ││                                                │
│ │ Altered mental   ││ TIMELINE (Last 7 Days)                         │
│ └──────────────────┘│ ├─ 3 min ago - Ambulance (ECG: ST elevation)  │
│                      │ ├─ 2 days ago - Apollo Hospital (Cardio F/U)  │
│ 🟡 URGENT (12)       │ ├─ 3 days ago - Labs (Cholesterol high)       │
│                      │ └─ 1 week ago - Pharmacy (Rx refill)           │
│ [Show all...]        │                                                │
│                      │ DATA SOURCES                                   │
│ 🟢 MINOR (8)         │ ✓ Ambulance  ✓ ABDM  ✓ Labs  ✓ Pharmacy       │
│                      │                                                │
│ [Show all...]        │ QUICK ACTIONS                                  │
│                      │ ┌───────┬───────┬───────┬───────┬───────┐    │
│                      │ │ ESI   │ ASSIGN│ CALL  │ ORDER │ NOTES │    │
│                      │ │ LEVEL │  BAY  │ SPEC  │ TESTS │       │    │
│                      │ └───────┴───────┴───────┴───────┴───────┘    │
│                      │                                                │
│                      │ [COMPLETE TRIAGE]                              │
│                      │                                                │
└──────────────────────┴───────────────────────────────────────────────┘
```

## Key Features

### 1. Touch-Optimized Interactions

**Tap Targets:**
- Minimum 44x44px (iOS), 48x48px (Android Material)
- Adequate spacing between buttons (8px minimum)
- Large text for glanceability (16px+ body, 20px+ headlines)

**Gestures:**
- **Swipe Right:** Mark patient as triaged
- **Swipe Left:** Defer to next (move to end of queue)
- **Swipe Up on Card:** Open full patient detail
- **Swipe Down:** Close detail, return to queue
- **Long Press:** Quick actions menu
- **Pull to Refresh:** Update queue

### 2. Offline-First Architecture

```javascript
// Service Worker for offline capability

// Cache Strategy:
1. CRITICAL DATA (Cache-First):
   - Patient queue (last sync)
   - Patient details already viewed
   - FHIR bundles already fetched
   - User preferences

2. DYNAMIC DATA (Network-First with Fallback):
   - Real-time vitals (if offline, show last known)
   - New ABDM data (queue fetch, sync when online)
   - Consent status

3. BACKGROUND SYNC:
   - Triage decisions made offline → sync when online
   - Notes/comments → sync on reconnect
   - Order requests → queue and sync

// UI Indicators:
- "📶 Online" (green) vs "⚠ Offline Mode" (amber)
- "↻ Syncing..." when reconnected
- "✓ Synced 2 min ago" confirmation
```

**Offline Workflow:**
1. Nurse starts shift, data pre-cached
2. Moves to area with poor connectivity
3. Continues triage using cached data
4. App shows "Offline Mode" indicator
5. All actions saved locally
6. Returns to wifi area
7. App auto-syncs all changes
8. Shows "✓ 5 patients synced" confirmation

### 3. Voice Input for Speed

```
VOICE COMMANDS:

"Triage level one critical" → Sets ESI Level 1
"Assign to trauma bay two" → Assigns patient to bay
"Order ECG and troponin" → Pre-selects common tests
"Allergic to penicillin" → Adds allergy alert
"Call cardiology" → Initiates specialist call

VOICE NOTES:
[🎤 Tap microphone]
"Patient reports crushing chest pain for thirty minutes,
 denies radiation, mild shortness of breath, no nausea"
→ Converts to text, editable before saving
```

### 4. Smart Defaults & Predictive Ordering

**Based on Chief Complaint:**
```
Chest Pain (Suspected Cardiac):
Auto-suggests:
- ☑ ECG (12-lead)
- ☑ Troponin
- ☑ CBC, BMP
- ☑ Chest X-Ray
- ☐ D-Dimer (optional)
- ☐ Lipid Panel (optional)

Abdominal Pain (Pregnant):
Auto-suggests:
- ☑ OB/GYN Consult
- ☑ Ultrasound
- ☑ CBC, Urinalysis
- ☑ hCG
```

Nurse can one-tap accept all or customize.

### 5. ABDM Integration (Mobile Workflow)

```python
# Mobile-optimized ABDM flow:

1. PATIENT IDENTIFICATION
   - Scan ABHA QR code with camera
   - Or manual entry with autocomplete
   - Or search by phone/name

2. BACKGROUND DATA FETCH
   # While nurse is taking vitals (first 30 seconds),
   # app fetches ABDM data in background:

   async def fetch_patient_abdm_data(abha_number):
       # Non-blocking, shows loading indicator
       discovery = await abdm_client.discover(abha_number)

       # Emergency consent (streamlined for triage)
       consent = await abdm_client.request_emergency_consent(
           abha_number,
           hi_types=["all"],  # Get everything available
           lookback_days=90
       )

       # Fetch and parse
       records = await abdm_client.fetch_records(consent.id)
       parsed = parse_fhir_for_mobile(records)

       # Update UI with push notification
       notify_user("✓ Medical history loaded from 2 hospitals")

       return parsed

3. PROGRESSIVE DISPLAY
   - Show data as it arrives (not all-or-nothing)
   - Critical info first: Allergies, active meds, recent visits
   - Full timeline loads in background
   - User can proceed with triage while data still loading
```

### 6. Notification System

**Push Notifications (if app backgrounded):**
- "🚨 New critical patient: Chest pain, BP 180/110"
- "⏱ Patient Rajesh Kumar waiting 15 min (Level 1)"
- "✓ Lab results ready for Priya Sharma"

**In-App Notifications:**
- Sliding banner from top
- Auto-dismiss after 5 seconds
- Tap to go directly to patient

**Haptic Feedback:**
- Vibration on critical patient arrival
- Subtle tap on successful action completion
- Distinct patterns for different alert types

### 7. Dark Mode (Essential for 24/7 Use)

```
AUTO-SWITCHING:
- 6am-6pm: Light mode
- 6pm-6am: Dark mode
- Or: Follow system preference
- Or: Manual toggle

DARK MODE COLORS:
- Background: #1A1A1A
- Cards: #2D2D2D
- Text: #F5F5F5
- RED (Critical): #FF6B6B (softer than daytime red)
- YELLOW: #FFD93D
- GREEN: #6BCF7F
- Reduce eye strain during night shifts
```

## Performance Optimization

### Bundle Size Targets
```
Initial Load: < 300KB (gzipped)
Time to Interactive: < 3 seconds on 3G
Lighthouse Score: 90+ (Mobile)

Lazy Loading:
- Timeline view (load when expanded)
- Full EMR (load on request)
- Charts/graphs (load when tab opened)
```

### Battery Optimization
```
- Reduce polling frequency when battery < 20%
- Pause real-time updates when app backgrounded
- Use efficient web sockets (not polling) for vitals
- Cache aggressively to reduce network requests
```

## Technology Stack

```javascript
Framework: React Native (iOS + Android native apps)
          or PWA (Progressive Web App) for web-based mobile

State: Redux Toolkit with RTK Query (offline support)
Offline: Redux Persist + Background Sync API
Voice: Web Speech API / React Native Voice
Camera: For QR code scanning (ABHA cards)
Push: FCM (Firebase Cloud Messaging) or OneSignal
Analytics: Mixpanel (track triage times, user flows)

// Native features needed:
- Camera access (QR scanning)
- Microphone (voice input)
- Vibration (haptic feedback)
- Background sync
- Push notifications
- Biometric auth (FaceID/TouchID for login)
```

## Strengths of This Concept

✅ **Mobile-First:** Works where triage actually happens (bedside)
✅ **Offline Capability:** No dependency on perfect connectivity
✅ **Speed:** Touch-optimized for rapid interaction
✅ **Voice Input:** Hands-free operation when needed
✅ **Portable:** Take device to patient, not vice versa
✅ **Battery Efficient:** Optimized for long shifts

## Limitations

❌ **Small Screen:** Less information visible at once
❌ **No Parallel View:** Can't monitor multiple critical patients simultaneously
❌ **Typing on Mobile:** Slower than desktop keyboard
❌ **Network Dependency:** Offline mode has limitations
❌ **App Installation:** Requires download/install (if native app)

## When to Use Patient-First Mobile

**Ideal for:**
- Triage nurses moving between patients
- Ambulance/pre-hospital triage
- Small to medium clinics (under 20 patients at once)
- Settings with intermittent connectivity
- Rapid assessment zones (bedside triage)

**Not ideal for:**
- Central queue monitoring (need desktop)
- High patient volumes (40+ concurrent)
- Complex data analysis requiring large screens
- Multi-patient parallel monitoring

## User Testing Metrics

**Success Criteria:**
- Triage completion time: < 90 seconds (match KatApp research)
- System Usability Scale (SUS): > 78
- User preference: > 70% prefer vs paper
- Offline sync accuracy: 100% (no data loss)
- Battery drain: < 15% per 8-hour shift

## Next Steps

1. **Build PWA prototype** (web-first, then native if needed)
2. **Test with 5 triage nurses** (observe workflow)
3. **Measure offline reliability** (simulate network drops)
4. **Voice input accuracy** (medical terminology)
5. **Iterate based on field testing**
