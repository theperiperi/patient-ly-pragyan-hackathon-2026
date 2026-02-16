# Frontend - Triage UI

Next.js application for emergency department triage. Provides patient intake (with voice input), real-time queue management, AI-powered triage decisions, and analytics dashboards.

## Setup

```bash
npm install
npm run dev
# Open http://localhost:3000
```

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Landing | Main entry point |
| `/intake` | Patient Intake | Register new patients via form or voice recording |
| `/queue` | Patient Queue | Real-time queue ordered by ESI acuity level |
| `/triage` | Triage View | AI triage decision with SBAR handoff, protocols, bay assignment |
| `/dashboard` | Analytics | KPIs, charts, and ED performance metrics |

### `/intake` - Patient Intake

Supports two input modes:
- **Form input** - Manual entry of patient demographics, chief complaint, and vitals
- **Voice input** - Record audio (or paste transcript), which is sent to the voice API for automatic extraction of patient data, vitals, conditions, and medications

The voice API returns FHIR-structured data that auto-populates the intake form.

### `/triage` - AI Triage Decision

Displays the full AI triage assessment:
- **ESI Level** (1-5) with color-coded acuity
- **Bay Assignment** (Resus Bay, Cardiac Bay, Treatment Room, Fast Track, etc.)
- **Specialists** to page
- **Clinical Protocols** to activate (Chest Pain Protocol, Stroke Protocol, etc.)
- **Labs and Imaging** to order
- **SBAR Handoff** (Situation, Background, Assessment, Recommendation)
- **Clinical Alerts** (drug interactions, allergies, high-risk conditions)
- **ABDM Data** - Conditions, medications, allergies, and encounters from patient's health record

### `/queue` - Patient Queue

Shows all patients ordered by acuity with:
- Color-coded priority (critical/urgent/minor)
- Current vitals and chief complaint
- Queue position and assigned bay
- Click to expand full triage details

### `/dashboard` - Analytics

ED performance metrics and visualizations using Recharts.

## Voice Integration

The frontend integrates with a voice processing backend for hands-free patient intake:

```
Browser microphone → WebM audio blob
  → POST /voice/ingest (FormData with audio file)
  → Backend: STT → NLP extraction → FHIR resource generation
  → Response: patient identity, vitals, conditions, medications
  → Auto-populate intake form
```

Text transcript input is also supported via `POST /voice/ingest/transcript`.

The voice API URL is configured via `NEXT_PUBLIC_VOICE_API_URL` environment variable.

## API Route

`POST /api/triage` - Server-side triage endpoint that proxies to the triage agent API. Accepts patient ID and chief complaint, returns the full AI triage decision matching the `Patient` interface.

## Tech Stack

- **Next.js 16** with App Router
- **React 19**
- **TypeScript 5**
- **Tailwind CSS 4** for styling
- **Shadcn/ui** component library (via Radix UI primitives)
- **Recharts** for dashboard charts
- **Lucide React** for icons
- **next-pwa** for Progressive Web App support

## Type Definitions

Core types in `lib/types.ts`:

- `Patient` - Full patient record (demographics, vitals, alerts, ABDM data, AI decision)
- `AIDecision` - Triage output (ESI, bay, specialists, protocols, labs, imaging, SBAR)
- `Vitals` - Six vital signs (BP, HR, SpO2, temp, RR, pain) with status and trend
- `ABDMData` - ABDM health record (conditions, medications, allergies, encounters)
- `SBARHandoff` - Structured clinical handoff (Situation, Background, Assessment, Recommendation)

## Directory Structure

```
frontend/
├── app/
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page
│   ├── globals.css              # Global styles
│   ├── api/
│   │   └── triage/route.ts      # Server-side triage API route
│   ├── intake/page.tsx          # Patient intake form + voice
│   ├── queue/page.tsx           # Patient queue management
│   ├── triage/page.tsx          # AI triage decision view
│   └── dashboard/page.tsx       # Analytics dashboard
├── components/
│   ├── triage/                  # Triage-specific components
│   └── ui/                      # Shadcn/ui component library
├── lib/
│   ├── types.ts                 # TypeScript type definitions
│   ├── utils.ts                 # Utility functions (cn, etc.)
│   ├── use-triage.ts            # Custom React hook for triage state
│   ├── voice-api.ts             # Voice API client (transcribe audio/text)
│   └── mock-data.ts             # Mock patient data for development
├── voice/
│   ├── api/                     # Voice API config
│   ├── extraction/              # Voice-to-structured-data extraction
│   └── stt/                     # Speech-to-text processing
├── public/
│   └── icons/                   # PWA icons
├── scripts/
│   └── generate-icons.mjs       # Icon generation script
├── ingest/
│   └── core/                    # Shared ingestion config
├── package.json
├── next.config.ts
├── vercel.json                  # Vercel deployment (rewrites for /voice, /health)
└── tsconfig.json
```

## Deployment

Configured for Vercel with rewrites in `vercel.json`:
- `/voice/:path*` - Proxied to voice processing backend
- `/health` - Health check endpoint

```bash
npm run build    # Production build
npm start        # Start production server
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_VOICE_API_URL` | Voice processing backend URL | `""` (relative) |
