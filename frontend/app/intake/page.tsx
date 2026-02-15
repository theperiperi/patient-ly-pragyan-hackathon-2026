"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, User, Heart, Stethoscope, Pill, FileText, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { VoiceInputButton } from "@/components/triage/voice-input-button";
import {
  transcribeAudio,
  parseVoiceResponse,
  ExtractedPatientData,
} from "@/lib/voice-api";
import { Badge } from "@/components/ui/badge";

type ProcessingState = "idle" | "recording" | "processing" | "done" | "error";

const LANGUAGES = [
  { code: "", label: "Auto-detect" },
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
  { code: "kn", label: "Kannada" },
  { code: "bn", label: "Bengali" },
  { code: "mr", label: "Marathi" },
  { code: "gu", label: "Gujarati" },
  { code: "ml", label: "Malayalam" },
  { code: "pa", label: "Punjabi" },
  { code: "ur", label: "Urdu" },
] as const;

// Whisper returns ISO 639-1 codes; map to display names
const LANGUAGE_NAMES: Record<string, string> = {
  en: "English", english: "English",
  hi: "Hindi", hindi: "Hindi",
  ta: "Tamil", tamil: "Tamil",
  te: "Telugu", telugu: "Telugu",
  kn: "Kannada", kannada: "Kannada",
  bn: "Bengali", bengali: "Bengali",
  mr: "Marathi", marathi: "Marathi",
  gu: "Gujarati", gujarati: "Gujarati",
  ml: "Malayalam", malayalam: "Malayalam",
  pa: "Punjabi", punjabi: "Punjabi",
  ur: "Urdu", urdu: "Urdu",
};

export default function IntakePage() {
  const router = useRouter();
  const [state, setState] = useState<ProcessingState>("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [data, setData] = useState<ExtractedPatientData | null>(null);
  const [language, setLanguage] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState<string | null>(null);

  // Editable fields (populated from voice, editable by user)
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState<"M" | "F" | "">("");
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [hr, setHr] = useState("");
  const [bpSys, setBpSys] = useState("");
  const [bpDia, setBpDia] = useState("");
  const [spo2, setSpo2] = useState("");
  const [temp, setTemp] = useState("");
  const [rr, setRr] = useState("");
  const [conditions, setConditions] = useState<string[]>([]);
  const [medications, setMedications] = useState<string[]>([]);
  const [transcript, setTranscript] = useState("");

  const populateFields = useCallback((d: ExtractedPatientData) => {
    setName(d.name);
    setAge(d.age != null ? String(d.age) : "");
    setGender(d.gender || "");
    setChiefComplaint(d.chiefComplaint);
    setHr(d.vitals.hr != null ? String(d.vitals.hr) : "");
    setBpSys(d.vitals.bpSystolic != null ? String(d.vitals.bpSystolic) : "");
    setBpDia(d.vitals.bpDiastolic != null ? String(d.vitals.bpDiastolic) : "");
    setSpo2(d.vitals.spo2 != null ? String(d.vitals.spo2) : "");
    setTemp(d.vitals.temp != null ? String(d.vitals.temp) : "");
    setRr(d.vitals.rr != null ? String(d.vitals.rr) : "");
    setConditions(d.conditions);
    setMedications(d.medications);
    setTranscript(d.transcript);
  }, []);

  const handleRecordingComplete = useCallback(
    async (audioBlob: Blob) => {
      setState("processing");
      setErrorMsg("");
      try {
        const response = await transcribeAudio(
          audioBlob,
          "recording.webm",
          language || undefined
        );
        const parsed = parseVoiceResponse(response);
        setData(parsed);
        setDetectedLanguage(parsed.detectedLanguage);
        populateFields(parsed);
        setState("done");
      } catch (err) {
        setErrorMsg(
          err instanceof Error ? err.message : "Failed to process audio"
        );
        setState("error");
      }
    },
    [populateFields, language]
  );

  const handleAddToQueue = () => {
    // In a real app this would POST to the backend.
    // For now we store in sessionStorage and redirect to queue.
    const patient = {
      name,
      age: parseInt(age) || 0,
      gender,
      chiefComplaint,
      vitals: {
        hr: hr ? parseFloat(hr) : null,
        bpSystolic: bpSys ? parseFloat(bpSys) : null,
        bpDiastolic: bpDia ? parseFloat(bpDia) : null,
        spo2: spo2 ? parseFloat(spo2) : null,
        temp: temp ? parseFloat(temp) : null,
        rr: rr ? parseFloat(rr) : null,
      },
      conditions,
      medications,
      transcript,
      addedAt: new Date().toISOString(),
    };
    const existing = JSON.parse(
      sessionStorage.getItem("voiceIntakePatients") || "[]"
    );
    existing.push(patient);
    sessionStorage.setItem("voiceIntakePatients", JSON.stringify(existing));
    router.push("/queue");
  };

  const hasMinimumData = name.trim().length > 0 || chiefComplaint.trim().length > 0;

  // Only pass external state when processing (API call in flight).
  // Otherwise leave it undefined so the button manages its own recording state.
  const voiceButtonState =
    state === "processing" ? ("processing" as const) : undefined;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b">
        <div className="max-w-2xl mx-auto px-4 py-2 flex items-center gap-2">
          <button
            onClick={() => router.back()}
            className="p-1.5 -ml-1.5 rounded hover:bg-muted"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span className="text-sm font-semibold">New Patient Intake</span>
          <Badge variant="secondary" className="h-5 text-[10px] ml-auto">
            Voice
          </Badge>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 pb-32">
        {/* Voice Input Section */}
        <div className="flex flex-col items-center py-8">
          <VoiceInputButton
            onRecordingComplete={handleRecordingComplete}
            state={voiceButtonState}
            size="lg"
          />
          {/* Language selector */}
          <div className="flex items-center gap-2 mt-4">
            <Globe className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="text-xs bg-slate-100 border border-slate-200 rounded-md px-2 py-1.5 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-300"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          {state === "idle" && !data && (
            <p className="text-xs text-muted-foreground mt-3 text-center max-w-[280px]">
              Speak in any language — describe the patient: name, age, symptoms, vitals, and history
            </p>
          )}
        </div>

        {/* Error */}
        {state === "error" && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 mb-6">
            <p className="text-sm text-red-700">{errorMsg}</p>
            <button
              onClick={() => setState("idle")}
              className="text-xs text-red-600 underline mt-1"
            >
              Try again
            </button>
          </div>
        )}

        {/* Transcript */}
        {transcript && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-slate-400" />
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Transcript
              </h3>
              {detectedLanguage && (
                <Badge variant="outline" className="h-4 text-[10px] bg-blue-50 border-blue-200 text-blue-600">
                  {LANGUAGE_NAMES[detectedLanguage.toLowerCase()] || detectedLanguage}
                </Badge>
              )}
            </div>
            <p className="text-sm text-slate-600 bg-slate-50 rounded-lg p-3 border border-slate-100 italic">
              &ldquo;{transcript}&rdquo;
            </p>
          </div>
        )}

        {/* Extracted/Editable Fields */}
        {(state === "done" || data) && (
          <div className="space-y-6">
            {/* Demographics */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <User className="w-4 h-4 text-slate-500" />
                <h3 className="text-sm font-semibold">Patient Details</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Patient name"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">
                      Age
                    </label>
                    <input
                      type="number"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      placeholder="Age"
                      className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">
                      Gender
                    </label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setGender("M")}
                        className={cn(
                          "flex-1 h-10 rounded-lg border text-sm font-medium transition-all",
                          gender === "M"
                            ? "bg-slate-800 text-white border-slate-800"
                            : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                        )}
                      >
                        Male
                      </button>
                      <button
                        onClick={() => setGender("F")}
                        className={cn(
                          "flex-1 h-10 rounded-lg border text-sm font-medium transition-all",
                          gender === "F"
                            ? "bg-slate-800 text-white border-slate-800"
                            : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                        )}
                      >
                        Female
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Chief Complaint */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Stethoscope className="w-4 h-4 text-slate-500" />
                <h3 className="text-sm font-semibold">Chief Complaint</h3>
              </div>
              <textarea
                value={chiefComplaint}
                onChange={(e) => setChiefComplaint(e.target.value)}
                placeholder="Primary symptom or reason for visit"
                rows={2}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300 resize-none"
              />
            </section>

            {/* Vitals */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Heart className="w-4 h-4 text-red-500" />
                <h3 className="text-sm font-semibold">Vitals</h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    Heart Rate (bpm)
                  </label>
                  <input
                    type="number"
                    value={hr}
                    onChange={(e) => setHr(e.target.value)}
                    placeholder="--"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    SpO2 (%)
                  </label>
                  <input
                    type="number"
                    value={spo2}
                    onChange={(e) => setSpo2(e.target.value)}
                    placeholder="--"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    BP Systolic (mmHg)
                  </label>
                  <input
                    type="number"
                    value={bpSys}
                    onChange={(e) => setBpSys(e.target.value)}
                    placeholder="--"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    BP Diastolic (mmHg)
                  </label>
                  <input
                    type="number"
                    value={bpDia}
                    onChange={(e) => setBpDia(e.target.value)}
                    placeholder="--"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    Temp (°C)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={temp}
                    onChange={(e) => setTemp(e.target.value)}
                    placeholder="--"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">
                    Resp Rate (/min)
                  </label>
                  <input
                    type="number"
                    value={rr}
                    onChange={(e) => setRr(e.target.value)}
                    placeholder="--"
                    className="w-full h-10 px-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300"
                  />
                </div>
              </div>
            </section>

            {/* Conditions */}
            {conditions.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <Stethoscope className="w-4 h-4 text-amber-500" />
                  <h3 className="text-sm font-semibold">Conditions</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {conditions.map((c, i) => (
                    <Badge
                      key={i}
                      variant="outline"
                      className="text-xs bg-amber-50 border-amber-200 text-amber-700"
                    >
                      {c}
                    </Badge>
                  ))}
                </div>
              </section>
            )}

            {/* Medications */}
            {medications.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <Pill className="w-4 h-4 text-blue-500" />
                  <h3 className="text-sm font-semibold">Medications</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {medications.map((m, i) => (
                    <Badge
                      key={i}
                      variant="outline"
                      className="text-xs bg-blue-50 border-blue-200 text-blue-700"
                    >
                      {m}
                    </Badge>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {/* Re-record prompt when done */}
        {state === "done" && (
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setState("idle");
                setData(null);
                setTranscript("");
              }}
              className="text-xs text-slate-500 underline hover:text-slate-700"
            >
              Re-record voice input
            </button>
          </div>
        )}
      </main>

      {/* Sticky Footer */}
      {(state === "done" || data) && (
        <footer className="fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur border-t z-40">
          <div className="max-w-2xl mx-auto px-4 pt-3 pb-4">
            <button
              onClick={handleAddToQueue}
              disabled={!hasMinimumData}
              className={cn(
                "w-full h-12 rounded-lg font-semibold text-sm transition-all",
                hasMinimumData
                  ? "bg-emerald-600 text-white hover:bg-emerald-700 active:scale-[0.98]"
                  : "bg-slate-100 text-slate-400 cursor-not-allowed"
              )}
            >
              Add to Triage Queue
            </button>
          </div>
        </footer>
      )}
    </div>
  );
}
