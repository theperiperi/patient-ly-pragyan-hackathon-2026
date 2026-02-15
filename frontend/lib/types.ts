// Patient and Triage Decision Types

export type AcuityLevel = "critical" | "urgent" | "minor";
export type ESILevel = 1 | 2 | 3 | 4 | 5;

export interface VitalSign {
  value: string | number;
  unit: string;
  status: "critical" | "warning" | "normal";
  trend?: "up" | "down" | "stable";
}

export interface Vitals {
  bp: VitalSign;
  hr: VitalSign;
  spo2: VitalSign;
  temp: VitalSign;
  rr: VitalSign;
  pain: VitalSign;
}

export interface Alert {
  type: "critical" | "warning" | "info";
  text: string;
}

export interface Condition {
  name: string;
  status: "active" | "resolved";
  source: string;
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
}

export interface Encounter {
  date: string;
  type: string;
  facility: string;
  summary: string;
}

export interface ABDMData {
  conditions: Condition[];
  medications: Medication[];
  allergies: string[];
  encounters: Encounter[];
}

export interface SBARHandoff {
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
}

export interface AIDecision {
  esi: ESILevel;
  acuityLabel: string;
  acuityColor: AcuityLevel;
  confidence: number;
  bay: string;
  queuePosition: number;
  specialists: string[];
  protocols: string[];
  labs: string[];
  imaging: string[];
  interventions: string[];
  isolation: string | null;
  reasoning: string[];
  sbar: SBARHandoff;
}

export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: "M" | "F";
  abha: string;
  arrivalTime: string;
  arrivalMode: "Ambulance" | "Walk-in" | "Referral";
  chiefComplaint: string;
  vitals: Vitals;
  alerts: Alert[];
  abdmData: ABDMData;
  aiDecision: AIDecision;
}
