# Interactive HTML Prototypes

## Overview

This directory contains **fully functional, self-contained HTML/CSS/JavaScript prototypes** for all four triage UI concepts. Each file is a complete, standalone prototype with mocked data and interactive features.

## Quick Start

**Open the index page:**
```bash
# From this directory:
open index.html

# Or from project root:
open ui-experiments/prototypes/html/index.html
```

The index page provides links to all four concepts with descriptions and stats.

## Prototypes

### ✅ Concept A: Command Center (COMPLETE)
**File:** `concept-a-command-center.html` (1,940 lines, 67KB)

**Features:**
- ✅ Dashboard with 28 patient queue
- ✅ Color-coded priority cards (RED/YELLOW/GREEN)
- ✅ Modal detail view for each patient
- ✅ Real-time vital signs (simulated)
- ✅ ABDM data source indicators
- ✅ Interactive quick actions
- ✅ Department status bar
- ✅ Search functionality
- ✅ Responsive design (desktop-optimized)

**Mock Data:**
- 3 critical patients (RED)
- 12 urgent patients (YELLOW)
- 8 minor patients (GREEN)
- 5 in-treatment patients (BLUE)
- Complete patient histories with FHIR-like data

**Interactions:**
- Click any patient card → Opens detailed modal
- Hover cards → Highlights
- Action buttons → Simulated triage workflow
- Department stats → Real-time updates (simulated)

---

### ✅ Concept B: Patient-First Mobile (COMPLETE)
**File:** `concept-b-mobile.html` (2,101 lines, 71KB)

**Features:**
- ✅ Mobile-optimized touch interface
- ✅ Large tap targets (44px+)
- ✅ Swipe gestures (left/right for actions)
- ✅ Bottom sheet action panel
- ✅ Offline mode simulation
- ✅ Dark mode toggle
- ✅ Voice input button (UI only)
- ✅ Battery status indicator
- ✅ Sync status
- ✅ Pull-to-refresh (simulated)

**Mock Data:**
- Same 28 patients as Concept A
- Optimized for single-patient focus
- Timeline in card format

**Interactions:**
- Tap patient card → Expands to full detail
- Swipe up → Action panel
- Swipe down → Dismiss
- Swipe left/right on cards → Quick actions (defer/triage)
- Toggle dark mode → Switches theme
- Pull down → Refresh animation

**Best Viewed On:**
- Mobile browser (iPhone/Android)
- Desktop browser with mobile emulation (DevTools → Device Toolbar)
- Recommended: iPhone 12 Pro / Pixel 5 viewport

---

### ✅ Concept C: Timeline-Centric (COMPLETE)
**File:** `concept-c-timeline.html` (1,337 lines, 47KB)

**Features:**
- ✅ Horizontal timeline (90 days)
- ✅ Interactive event markers
- ✅ Swim lanes (encounters, labs, meds, vitals)
- ✅ Zoom controls (24h/7d/30d/90d)
- ✅ Event detail panel
- ✅ Trend charts (BP, Lab results)
- ✅ Canvas-based visualizations
- ✅ AI risk assessment panel
- ✅ Multi-source data indicators

**Mock Data:**
- Patient: Rajesh Kumar, 45M (cardiac patient)
- 90-day medical history
- 8 timeline events (ambulance, hospital visits, labs)
- Blood pressure trends
- HbA1c lab trends
- Medication timeline

**Interactions:**
- Click timeline event → Shows detail panel
- Zoom buttons → Change time scale (visual update)
- Hover events → Tooltip preview
- Charts → Interactive (hover for values)
- Scroll timeline → Pan left/right

**Visualizations:**
- Canvas-based BP chart (line graph)
- Canvas-based HbA1c chart (bar graph)
- SVG timeline with markers
- Color-coded event types

---

### ✅ Concept D: Hybrid Split-View (COMPLETE)
**File:** `concept-d-hybrid.html` (1,780 lines, 59KB)

**Features:**
- ✅ Persistent split-screen (40% queue / 60% detail)
- ✅ Resizable divider (drag to adjust split)
- ✅ Queue always visible
- ✅ Patient detail updates on click
- ✅ Comparison mode (view 2 patients side-by-side)
- ✅ Collapse/expand panels
- ✅ Multi-user awareness simulation
- ✅ Smart prefetch indicator
- ✅ Real-time collaboration status

**Mock Data:**
- Same 28 patients
- Dual-patient comparison data
- User presence indicators

**Interactions:**
- Click patient in queue → Detail panel updates
- Drag divider → Resize panels
- Collapse buttons → Hide/show panels
- Compare mode toggle → Split detail into 2 patients
- Click "View 2nd Patient" → Loads comparison
- User avatars → Show who's viewing

**Keyboard Shortcuts (Simulated):**
- ↑/↓ - Navigate patients
- Enter - Select patient
- C - Comparison mode
- [ - Collapse queue
- ] - Collapse detail

---

## Technical Details

### Architecture
All prototypes are **self-contained single-file HTML documents** with:
- Inline CSS (no external stylesheets)
- Inline JavaScript (no external libraries or frameworks)
- Embedded mock data (JSON structures)
- No server dependencies (open directly in browser)

### Mock Data Structure
```javascript
const patients = [
    {
        id: 1,
        name: "Rajesh Kumar",
        age: 45,
        gender: "M",
        abha: "22-7225-4829-5255",
        priority: "critical",
        complaint: "Chest pain, SOB",
        vitals: {
            bp: { systolic: 180, diastolic: 110, status: "critical" },
            hr: { value: 125, status: "high" },
            spo2: { value: 94, status: "low" },
            temp: { value: 98.6, status: "normal" },
            rr: { value: 22, status: "elevated" }
        },
        alerts: [
            { type: "critical", text: "Previous MI 2 years ago" },
            { type: "warning", text: "Diabetic on insulin" },
            { type: "allergy", text: "Penicillin - Anaphylaxis" }
        ],
        medications: [...],
        timeline: [...],
        abdmSources: ["Ambulance", "Apollo Hospital", "Labs", "Pharmacy"]
    },
    // ... 27 more patients
]
```

### Simulated ABDM Integration
Each prototype simulates ABDM data integration:
- **Discovery:** Patient identified by ABHA number
- **Data Sources:** Shows which HIPs contributed data (Apollo, AIIMS, etc.)
- **FHIR Bundles:** Mock data structured like FHIR resources
- **Timeline:** Encounters, DiagnosticReports, Medications from multiple sources
- **Consent:** Visual indicators of data access permissions

### Interactions & Animations
- **CSS Transitions:** Smooth hover effects, modal animations
- **JavaScript:** Event handling, DOM manipulation, data filtering
- **Canvas API:** Charts and graphs (Concepts C)
- **Touch Events:** Swipe gestures (Concept B)
- **Drag & Drop:** Resizable panels (Concept D)

### Browser Compatibility
Tested and working on:
- ✅ Chrome 120+
- ✅ Firefox 120+
- ✅ Safari 17+
- ✅ Edge 120+
- ✅ Mobile Safari (iOS 17+)
- ✅ Chrome Mobile (Android 13+)

### Performance
All prototypes are optimized for performance:
- No external HTTP requests (all assets inline/embedded)
- Minimal DOM manipulation
- Efficient event delegation
- CSS-based animations (GPU-accelerated)
- Canvas rendering for complex visualizations

---

## Viewing the Prototypes

### Desktop
1. **Double-click any `.html` file** to open in default browser
2. Or **drag & drop** file into browser window
3. Or use command line:
   ```bash
   open concept-a-command-center.html
   # Mac

   start concept-a-command-center.html
   # Windows

   xdg-open concept-a-command-center.html
   # Linux
   ```

### Mobile
**Option 1: Local Server**
```bash
# Python 3
python3 -m http.server 8000

# Then open on mobile:
# http://YOUR_IP:8000/concept-b-mobile.html
```

**Option 2: GitHub Pages**
If pushed to GitHub, prototypes are viewable at:
```
https://theperiperi.github.io/patient-ly-pragyan-hackathon-2026/ui-experiments/prototypes/html/index.html
```

**Option 3: File Transfer**
- AirDrop files to iPhone/iPad (Mac)
- Email files to yourself, open in mobile browser
- Use cloud storage (Dropbox, Drive, etc.)

---

## Prototype Comparison

| Feature | A: Command | B: Mobile | C: Timeline | D: Hybrid |
|---------|-----------|-----------|-------------|-----------|
| **Lines of Code** | 1,940 | 2,101 | 1,337 | 1,780 |
| **File Size** | 67 KB | 71 KB | 47 KB | 59 KB |
| **Platform** | Desktop | Mobile | Desktop | Desktop |
| **Mock Patients** | 28 | 28 | 1 (detailed) | 28 |
| **Interactivity** | High | Very High | High | Very High |
| **Animations** | Medium | High | Medium | Medium |
| **Touch Support** | No | Yes | No | No |
| **Dark Mode** | No | Yes | Yes | No |
| **Charts** | No | No | Yes (Canvas) | No |
| **Comparison Mode** | No | No | No | Yes |

---

## Development Notes

### File Structure
```
html/
├── index.html                     # Landing page with all concepts
├── concept-a-command-center.html  # Desktop dashboard
├── concept-b-mobile.html          # Mobile-first
├── concept-c-timeline.html        # Timeline visualization
├── concept-d-hybrid.html          # Split-view hybrid
└── README.md                      # This file
```

### Mock Data Sources
Patient data is modeled after:
- **ABDM DevKit** generated patients (100 realistic Indian scenarios)
- **FHIR Implementation Guide** v6.5.0 (ABDM)
- **Real-world triage protocols** (AIIMS ATP, ESI)
- **Research findings** (from triage-systems-research.md)

### Future Enhancements
Potential additions (not yet implemented):
- [ ] WebSocket simulation for real-time updates
- [ ] Service Worker for true offline mode
- [ ] IndexedDB for local data persistence
- [ ] Speech Recognition API for voice input (Concept B)
- [ ] WebRTC for multi-user collaboration (Concept D)
- [ ] Progressive Web App manifest

---

## Demo Scenarios

### Scenario 1: Critical Patient Triage (Concept A)
1. Open `concept-a-command-center.html`
2. Observe 3 RED patients at top
3. Click "Rajesh Kumar, 45M" (first critical)
4. Modal opens with full details
5. Review ambulance ECG, vitals, history
6. Click "Assign to Resus Bay 1"
7. Click "Call Cardiology"
8. Click "Complete Triage"
9. Patient card updates with assignment

### Scenario 2: Mobile Bedside Triage (Concept B)
1. Open `concept-b-mobile.html` in mobile browser
2. Toggle dark mode (top right)
3. Tap "Priya Sharma, 28F" (pregnant, abdominal pain)
4. Swipe up to open action panel
5. Select ESI Level 1 (Critical)
6. Tap "Assign to OB Bay"
7. Tap "Call OB/GYN"
8. Tap "Complete Triage"
9. Swipe down to return to queue

### Scenario 3: Timeline Analysis (Concept C)
1. Open `concept-c-timeline.html`
2. View horizontal timeline (90 days)
3. Click "2 DAYS AGO - Apollo Hospital"
4. Detail panel shows cardiology visit
5. Scroll down to BP trend chart
6. Observe sudden spike today vs stable 90 days
7. Review AI assessment (92% STEMI confidence)
8. Click zoom buttons (30d → 7d → 24h)
9. Timeline rescales (visual update)

### Scenario 4: Split-View Comparison (Concept D)
1. Open `concept-d-hybrid.html`
2. Queue visible on left, detail on right
3. Click "Rajesh Kumar" in queue → Detail updates
4. Click "Priya Sharma" → Detail switches
5. Drag divider left/right → Resize panels
6. Click "Compare Mode" button
7. Two patients shown side-by-side
8. Review vitals comparison (BP high vs low)
9. Click "Exit Compare" → Return to single view

---

## Keyboard Shortcuts (Concept D Only)

| Key | Action |
|-----|--------|
| ↑ | Previous patient in queue |
| ↓ | Next patient in queue |
| Enter | Select patient |
| C | Toggle comparison mode |
| [ | Collapse queue panel |
| ] | Collapse detail panel |
| Esc | Close modal/panel |

*(Simulated - visual feedback only in prototype)*

---

## For Hackathon Demo

**Recommended Demo Flow:**
1. **Start with Index** (`index.html`)
   - Show all 4 concepts on landing page
   - Explain each approach briefly

2. **Demo Concept B (Mobile)**
   - Most impressive for judges (touch, gestures, dark mode)
   - Show offline mode indicator
   - Demonstrate swipe actions
   - Toggle dark mode live

3. **Demo Concept C (Timeline)**
   - Visual wow factor (charts, timeline)
   - Show AI insights panel
   - Demonstrate trend analysis
   - Explain multi-source data aggregation

4. **Demo Concept A or D (Desktop)**
   - Show queue management at scale
   - Demonstrate rapid triage workflow
   - Highlight ABDM integration indicators

5. **Close with Impact**
   - "60-90 second triage vs 10-15 minute manual process"
   - "ABDM integration brings all patient data together"
   - "Mobile + Desktop = works where triage happens"

---

## Files Generated By

These prototypes were generated as part of the **Patient.ly ABDM Triage System** project for Pragyan Hackathon 2026. They are based on:

- UI Concept Documents (../CONCEPT_*.md)
- Research (../../research/triage-systems-research.md)
- ABDM DevKit (../../abdm-local-dev-kit/)

**Status:** ✅ All 4 Concepts Complete
**Last Updated:** February 15, 2026
**Total Lines:** 7,158 lines of HTML/CSS/JS
**Total Size:** 244 KB (all 4 files)

---

## Quick Links

- [Index Page](index.html) - Launch all prototypes
- [Concept A: Command Center](concept-a-command-center.html)
- [Concept B: Patient-First Mobile](concept-b-mobile.html)
- [Concept C: Timeline-Centric](concept-c-timeline.html)
- [Concept D: Hybrid Split-View](concept-d-hybrid.html)

---

**Happy Prototyping! 🏥📱💻**
