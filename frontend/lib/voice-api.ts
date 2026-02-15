// Voice API client for the voice ingestion backend

const VOICE_API_URL =
  process.env.NEXT_PUBLIC_VOICE_API_URL || "";

// --- Response types from voice API ---

export interface VoiceVitals {
  heart_rate: number | null;
  blood_pressure_systolic: number | null;
  blood_pressure_diastolic: number | null;
  spo2: number | null;
  temperature: number | null;
  respiratory_rate: number | null;
  body_weight: number | null;
  body_height: number | null;
  bmi: number | null;
}

export interface VoiceDiagnosis {
  code: string | null;
  description: string;
  clinical_status: string;
  onset_date: string | null;
}

export interface VoicePatientIdentity {
  full_name: string | null;
  birth_date: string | null;
  gender: string | null;
  mrn: string | null;
  abha_id: string | null;
}

export interface VoiceIngestResponse {
  source_type: string;
  transcript: string | null;
  detected_language: string | null;
  patient_identity: VoicePatientIdentity;
  chief_complaint: string | null;
  medications: string[];
  patient_resource: Record<string, unknown> | null;
  resources_count: number;
  resources: Record<string, unknown>[];
}

// --- Extracted form data (parsed from API response + resources) ---

export interface ExtractedPatientData {
  name: string;
  birthDate: string;
  age: number | null;
  gender: "M" | "F" | null;
  mrn: string;
  abhaId: string;
  chiefComplaint: string;
  vitals: {
    hr: number | null;
    bpSystolic: number | null;
    bpDiastolic: number | null;
    spo2: number | null;
    temp: number | null;
    rr: number | null;
  };
  conditions: string[];
  medications: string[];
  transcript: string;
  detectedLanguage: string | null;
}

function computeAge(birthDate: string): number | null {
  if (!birthDate) return null;
  const birth = new Date(birthDate);
  if (isNaN(birth.getTime())) return null;
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

function parseGender(gender: string | null): "M" | "F" | null {
  if (!gender) return null;
  const g = gender.toLowerCase();
  if (g === "male" || g === "m") return "M";
  if (g === "female" || g === "f") return "F";
  return null;
}

function extractVitalsFromResources(
  resources: Record<string, unknown>[]
): ExtractedPatientData["vitals"] {
  const vitals: ExtractedPatientData["vitals"] = {
    hr: null,
    bpSystolic: null,
    bpDiastolic: null,
    spo2: null,
    temp: null,
    rr: null,
  };

  for (const r of resources) {
    if (r.resourceType !== "Observation") continue;
    const coding = (r as any).code?.coding?.[0];
    if (!coding?.code) continue;

    const value = (r as any).valueQuantity?.value ?? null;

    switch (coding.code) {
      case "8867-4": // Heart rate
        vitals.hr = value;
        break;
      case "2708-6": // SpO2
      case "59408-5":
        vitals.spo2 = value;
        break;
      case "8310-5": // Temperature
        vitals.temp = value;
        break;
      case "9279-1": // Respiratory rate
        vitals.rr = value;
        break;
      case "85354-9": // Blood pressure panel
        for (const comp of (r as any).component || []) {
          const cc = comp?.code?.coding?.[0]?.code;
          const cv = comp?.valueQuantity?.value;
          if (cc === "8480-6") vitals.bpSystolic = cv;
          if (cc === "8462-4") vitals.bpDiastolic = cv;
        }
        break;
    }
  }

  return vitals;
}

function extractConditionsFromResources(
  resources: Record<string, unknown>[]
): string[] {
  const conditions: string[] = [];
  for (const r of resources) {
    if (r.resourceType !== "Condition") continue;
    const text =
      (r as any).code?.text ||
      (r as any).code?.coding?.[0]?.display ||
      "";
    if (text) conditions.push(text);
  }
  return conditions;
}

export function parseVoiceResponse(
  response: VoiceIngestResponse
): ExtractedPatientData {
  const identity = response.patient_identity;
  const birthDate = identity.birth_date || "";

  return {
    name: identity.full_name || "",
    birthDate,
    age: computeAge(birthDate),
    gender: parseGender(identity.gender),
    mrn: identity.mrn || "",
    abhaId: identity.abha_id || "",
    chiefComplaint: response.chief_complaint || "",
    vitals: extractVitalsFromResources(response.resources),
    conditions: extractConditionsFromResources(response.resources),
    medications: response.medications || [],
    transcript: response.transcript || "",
    detectedLanguage: response.detected_language || null,
  };
}

// --- API functions ---

export async function transcribeAudio(
  audioBlob: Blob,
  filename = "recording.webm",
  language?: string
): Promise<VoiceIngestResponse> {
  const formData = new FormData();
  formData.append("file", audioBlob, filename);
  if (language) {
    formData.append("language", language);
  }

  const res = await fetch(`${VOICE_API_URL}/voice/ingest`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Voice API error (${res.status}): ${detail}`);
  }

  return res.json();
}

export async function transcribeText(
  transcript: string
): Promise<VoiceIngestResponse> {
  const formData = new FormData();
  formData.append("transcript", transcript);

  const res = await fetch(`${VOICE_API_URL}/voice/ingest/transcript`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Voice API error (${res.status}): ${detail}`);
  }

  return res.json();
}
