"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { mockPatients } from "@/lib/mock-data";
import { Patient, AIDecision, Alert } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { ManualReviewModal, SwipeableCard } from "@/components/triage";
import { cn } from "@/lib/utils";
import {
  Clock,
  AlertTriangle,
  Filter,
  Ambulance,
  Building,
  Users,
  CheckCircle2,
  Timer,
  Activity,
  Brain,
  Loader2,
  Search,
  FileText,
  Stethoscope,
  ClipboardList,
  Sparkles,
  Check,
} from "lucide-react";

type FilterType = "all" | "critical" | "pending" | "approved" | "triaging";
type SortType = "acuity" | "arrival" | "wait";

interface QueuePatient extends Patient {
  status: "pending" | "in-review" | "approved" | "triaging";
  waitTime: string;
}

// AI Triage steps with icons
const triageSteps = [
  { id: "vitals", label: "Analyzing vitals", icon: Activity, duration: 1500 },
  { id: "history", label: "Fetching ABDM records", icon: FileText, duration: 2000 },
  { id: "symptoms", label: "Evaluating symptoms", icon: Stethoscope, duration: 1800 },
  { id: "protocols", label: "Matching protocols", icon: ClipboardList, duration: 1200 },
  { id: "esi", label: "Determining ESI level", icon: AlertTriangle, duration: 1000 },
  { id: "recommendations", label: "Generating recommendations", icon: Sparkles, duration: 1500 },
];

// Mock AI decision generator based on chief complaint
function generateMockAIDecision(chiefComplaint: string): AIDecision {
  const isCardiac = chiefComplaint.toLowerCase().includes("chest") || chiefComplaint.toLowerCase().includes("heart");
  const isRespiratory = chiefComplaint.toLowerCase().includes("breath") || chiefComplaint.toLowerCase().includes("cough");
  const isSevere = chiefComplaint.toLowerCase().includes("severe") || chiefComplaint.toLowerCase().includes("radiating");

  const esi = isCardiac && isSevere ? 2 : isCardiac || isRespiratory ? 3 : 4;

  return {
    esi,
    acuityLabel: esi === 2 ? "EMERGENT" : esi === 3 ? "MODERATE" : "LESS URGENT",
    acuityColor: esi <= 2 ? "critical" : esi === 3 ? "urgent" : "minor",
    confidence: 85 + Math.floor(Math.random() * 10),
    bay: esi === 2 ? "Cardiac Bay" : esi === 3 ? "Treatment Room 2" : "Fast Track",
    queuePosition: esi,
    specialists: isCardiac ? ["Cardiology"] : [],
    protocols: isCardiac ? ["Chest Pain Protocol"] : isRespiratory ? ["Respiratory Protocol"] : [],
    labs: ["CBC", "BMP", ...(isCardiac ? ["Troponin", "BNP"] : [])],
    imaging: isCardiac ? ["ECG", "Chest X-ray"] : isRespiratory ? ["Chest X-ray"] : [],
    interventions: ["IV Access", ...(isCardiac ? ["Cardiac monitoring"] : [])],
    isolation: null,
    reasoning: [
      `Patient presenting with ${chiefComplaint}`,
      isCardiac ? "Cardiac workup indicated" : "Standard evaluation needed",
      `ESI-${esi} classification based on presentation`,
    ],
    sbar: {
      situation: `Patient with ${chiefComplaint}`,
      background: "Medical history being reviewed",
      assessment: esi <= 2 ? "High acuity, requires immediate attention" : "Stable, requires evaluation",
      recommendation: `Assign to ${esi === 2 ? "Cardiac Bay" : esi === 3 ? "Treatment Room" : "Fast Track"}`
    }
  };
}

// Triaging patient card component
function TriagingPatientCard({
  patient,
  onComplete,
}: {
  patient: Partial<QueuePatient> & { name: string; age: number; gender: string; chiefComplaint: string; arrivalMode: string; arrivalTime: string };
  onComplete: (decision: AIDecision) => void;
}) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const ArrivalIcon = arrivalModeIcons[patient.arrivalMode as keyof typeof arrivalModeIcons] || Building;

  // Progress through animation steps
  useEffect(() => {
    if (currentStep >= triageSteps.length) {
      // All steps complete, generate mock decision and trigger callback
      const mockDecision = generateMockAIDecision(patient.chiefComplaint);
      const timer = setTimeout(() => onComplete(mockDecision), 500);
      return () => clearTimeout(timer);
    }

    const step = triageSteps[currentStep];
    const timer = setTimeout(() => {
      setCompletedSteps((prev) => [...prev, step.id]);
      setCurrentStep((prev) => prev + 1);
    }, step.duration);

    return () => clearTimeout(timer);
  }, [currentStep, onComplete, patient.chiefComplaint]);

  const progress = (completedSteps.length / triageSteps.length) * 100;

  return (
    <div className="border rounded-lg p-3 border-violet-300 bg-gradient-to-r from-violet-50/80 to-purple-50/80">
      <div className="flex items-start gap-3">
        {/* AI Processing indicator */}
        <div className="w-11 h-11 rounded-lg flex flex-col items-center justify-center flex-shrink-0 bg-violet-600 text-white relative overflow-hidden">
          <Brain className="w-5 h-5 animate-pulse" />
          <div
            className="absolute bottom-0 left-0 right-0 bg-violet-400 transition-all duration-300"
            style={{ height: `${progress}%`, opacity: 0.5 }}
          />
        </div>

        {/* Patient Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="font-semibold text-sm">{patient.name}</span>
            <span className="text-xs text-muted-foreground">
              {patient.age}{patient.gender}
            </span>
            <Badge className="h-4 text-[9px] bg-violet-100 text-violet-700 border-violet-200 animate-pulse">
              <Loader2 className="w-2.5 h-2.5 mr-0.5 animate-spin" />
              AI Triaging
            </Badge>
          </div>

          <p className="text-xs text-slate-600 truncate mb-1.5">
            {patient.chiefComplaint}
          </p>

          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
            <span className="flex items-center gap-1">
              <ArrivalIcon className="w-3 h-3" />
              {patient.arrivalMode}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {patient.arrivalTime}
            </span>
          </div>
        </div>
      </div>

      {/* AI Processing Steps */}
      <div className="mt-3 pt-2 border-t border-violet-200/50">
        <div className="space-y-1">
          {triageSteps.map((step, index) => {
            const StepIcon = step.icon;
            const isCompleted = completedSteps.includes(step.id);
            const isActive = index === currentStep;

            return (
              <div
                key={step.id}
                className={cn(
                  "flex items-center gap-2 text-[10px] transition-all duration-300",
                  isCompleted && "text-emerald-600",
                  isActive && "text-violet-700 font-medium",
                  !isCompleted && !isActive && "text-slate-400"
                )}
              >
                <div className="w-4 h-4 flex items-center justify-center">
                  {isCompleted ? (
                    <Check className="w-3 h-3" />
                  ) : isActive ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <StepIcon className="w-3 h-3" />
                  )}
                </div>
                <span>{step.label}</span>
                {isActive && (
                  <span className="ml-auto text-[9px] text-violet-500">processing...</span>
                )}
                {isCompleted && (
                  <span className="ml-auto text-[9px] text-emerald-500">done</span>
                )}
              </div>
            );
          })}
        </div>

        {/* Progress bar */}
        <div className="mt-2 h-1 bg-violet-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-violet-500 transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}

// New patient being triaged (partial data - AI is still processing)
const triagingPatient = {
  id: "triaging-001",
  name: "Ganesh Bhat",
  age: 57,
  gender: "M" as const,
  chiefComplaint: "Chest pain radiating to left arm",
  arrivalMode: "Ambulance" as const,
  arrivalTime: "Just now",
  waitTime: "0m",
  status: "triaging" as const,
};

// Extend mock patients with queue-specific data
const queuePatients: QueuePatient[] = mockPatients.map((p, i) => ({
  ...p,
  status: i === 0 ? "in-review" : "pending",
  waitTime: i === 0 ? "12m" : i === 1 ? "8m" : "3m",
})) as QueuePatient[];

const esiConfig = {
  1: { label: "ESI-1", color: "bg-red-600 text-white", priority: "Resuscitation" },
  2: { label: "ESI-2", color: "bg-red-500 text-white", priority: "Emergent" },
  3: { label: "ESI-3", color: "bg-amber-500 text-white", priority: "Urgent" },
  4: { label: "ESI-4", color: "bg-emerald-600 text-white", priority: "Less Urgent" },
  5: { label: "ESI-5", color: "bg-emerald-500 text-white", priority: "Non-Urgent" },
};

const arrivalModeIcons = {
  Ambulance: Ambulance,
  "Walk-in": Building,
  Referral: Building,
};

export default function QueuePage() {
  const router = useRouter();
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("acuity");
  const [patients, setPatients] = useState(queuePatients);
  const [manualReviewPatient, setManualReviewPatient] = useState<QueuePatient | null>(null);
  const [currentTriaging, setCurrentTriaging] = useState<typeof triagingPatient | null>(triagingPatient);

  // Handle triaging complete - convert to full patient
  const handleTriagingComplete = useCallback((aiDecision: AIDecision) => {
    if (!currentTriaging) return;

    // Build the completed patient using the AI decision from the agent
    // Note: vitals, abdmData are mocked since they come from triage nurse input
    const completedPatient: QueuePatient = {
      id: currentTriaging.id,
      name: currentTriaging.name,
      age: currentTriaging.age,
      gender: currentTriaging.gender,
      abha: "52-7225-4829-5255",  // Would come from patient lookup
      chiefComplaint: currentTriaging.chiefComplaint,
      arrivalMode: currentTriaging.arrivalMode,
      arrivalTime: "1 min ago",
      waitTime: "1m",
      status: "pending",
      // Vitals are mocked - would come from triage nurse input
      vitals: {
        bp: { value: "120/80", unit: "mmHg", status: "normal", trend: "stable" },
        hr: { value: 82, unit: "bpm", status: "normal", trend: "stable" },
        spo2: { value: 98, unit: "%", status: "normal", trend: "stable" },
        temp: { value: 98.6, unit: "°F", status: "normal", trend: "stable" },
        rr: { value: 16, unit: "/min", status: "normal", trend: "stable" },
        pain: { value: "5/10", unit: "", status: "warning", trend: "stable" },
      },
      // Alerts from AI decision
      alerts: (aiDecision.alerts || []).map((alert: Alert) => ({
        type: alert.type as "critical" | "warning" | "info",
        text: alert.text
      })),
      // ABDM data mocked - would come from MCP in a full integration
      abdmData: {
        conditions: [],
        medications: [],
        allergies: [],
        encounters: [],
      },
      // AI Decision from the triage agent
      aiDecision: {
        esi: aiDecision.esi,
        acuityLabel: aiDecision.acuityLabel,
        acuityColor: aiDecision.acuityColor as "critical" | "urgent" | "minor",
        confidence: aiDecision.confidence,
        bay: aiDecision.bay,
        queuePosition: aiDecision.queuePosition,
        specialists: aiDecision.specialists || [],
        protocols: aiDecision.protocols || [],
        labs: aiDecision.labs || [],
        imaging: aiDecision.imaging || [],
        interventions: aiDecision.interventions || [],
        isolation: aiDecision.isolation,
        reasoning: aiDecision.reasoning || [],
        sbar: aiDecision.sbar || {
          situation: "",
          background: "",
          assessment: "",
          recommendation: ""
        },
      },
    };

    setPatients((prev) => [completedPatient, ...prev]);
    setCurrentTriaging(null);
  }, [currentTriaging]);

  const stats = {
    total: patients.length + (currentTriaging ? 1 : 0),
    critical: patients.filter((p) => p.aiDecision.esi <= 2).length,
    pending: patients.filter((p) => p.status === "pending").length,
    approved: patients.filter((p) => p.status === "approved").length,
    triaging: currentTriaging ? 1 : 0,
  };

  const filteredPatients = patients
    .filter((p) => {
      if (filter === "critical") return p.aiDecision.esi <= 2;
      if (filter === "pending") return p.status === "pending";
      if (filter === "approved") return p.status === "approved";
      return true;
    })
    .sort((a, b) => {
      if (sort === "acuity") return a.aiDecision.esi - b.aiDecision.esi;
      return 0;
    });

  const handlePatientTap = (index: number) => {
    router.push(`/triage?patient=${index}`);
  };

  const handleApprove = (patientId: string) => {
    setPatients((prev) =>
      prev.map((p) =>
        p.id === patientId ? { ...p, status: "approved" as const } : p
      )
    );
  };

  const handleManualReview = (patient: QueuePatient) => {
    setManualReviewPatient(patient);
  };

  const handleConfirmManualReview = (reason: string, priority: "urgent" | "standard") => {
    console.log(`Manual review for ${manualReviewPatient?.name}:`, { reason, priority });
    setManualReviewPatient(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-slate-600" />
              <h1 className="text-base font-semibold">Triage Queue</h1>
            </div>
            <div className="flex items-center gap-1.5 text-[10px]">
              <span className="flex items-center gap-1 px-2 py-1 rounded bg-slate-100 text-slate-600">
                <Users className="w-3 h-3" />
                {stats.total} total
              </span>
              <span className="flex items-center gap-1 px-2 py-1 rounded bg-red-50 text-red-700">
                <AlertTriangle className="w-3 h-3" />
                {stats.critical} critical
              </span>
              <span className="flex items-center gap-1 px-2 py-1 rounded bg-amber-50 text-amber-700">
                <Timer className="w-3 h-3" />
                {stats.pending} pending
              </span>
              {stats.triaging > 0 && (
                <span className="flex items-center gap-1 px-2 py-1 rounded bg-violet-50 text-violet-700">
                  <Brain className="w-3 h-3 animate-pulse" />
                  {stats.triaging} triaging
                </span>
              )}
              {!currentTriaging && (
                <button
                  onClick={() => {
                    // Sample mock patients with varied complaints
                    const samplePatients = [
                      { name: "Ganesh Bhat", age: 57, chiefComplaint: "Chest pain radiating to left arm" },
                      { name: "Ashok Mehta", age: 65, chiefComplaint: "High fever with chills" },
                      { name: "Rohit Nair", age: 42, chiefComplaint: "Severe abdominal pain" },
                      { name: "Priya Sharma", age: 38, chiefComplaint: "Shortness of breath" },
                    ];
                    const patient = samplePatients[Math.floor(Math.random() * samplePatients.length)];
                    setCurrentTriaging({
                      ...triagingPatient,
                      id: `triaging-${Date.now()}`,
                      name: patient.name,
                      age: patient.age,
                      chiefComplaint: patient.chiefComplaint,
                    });
                  }}
                  className="flex items-center gap-1 px-2 py-1 rounded bg-violet-100 text-violet-700 hover:bg-violet-200 transition-colors text-[10px] font-medium"
                >
                  <Sparkles className="w-3 h-3" />
                  Simulate Arrival
                </button>
              )}
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <div className="flex gap-1 flex-wrap">
              {(["all", "critical", "pending"] as FilterType[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "px-2.5 py-1 rounded text-[11px] font-medium capitalize transition-colors",
                    filter === f
                      ? "bg-slate-800 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  {f}
                </button>
              ))}
              {stats.triaging > 0 && (
                <button
                  onClick={() => setFilter("triaging")}
                  className={cn(
                    "px-2.5 py-1 rounded text-[11px] font-medium capitalize transition-colors",
                    filter === "triaging"
                      ? "bg-violet-600 text-white"
                      : "bg-violet-100 text-violet-700 hover:bg-violet-200"
                  )}
                >
                  triaging
                </button>
              )}
            </div>
            <div className="w-px h-4 bg-slate-200 mx-1" />
            <div className="flex gap-1">
              {(["acuity", "arrival", "wait"] as SortType[]).map((s) => (
                <button
                  key={s}
                  onClick={() => setSort(s)}
                  className={cn(
                    "px-2.5 py-1 rounded text-[11px] font-medium capitalize transition-colors",
                    sort === s
                      ? "bg-slate-800 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Patient List */}
      <main className="max-w-3xl mx-auto px-4 py-3">
        <p className="text-[10px] text-muted-foreground text-center mb-2">
          Swipe right to approve • Swipe left for manual review • Tap for details
        </p>
        <div className="space-y-2">
          {/* Show triaging patient at the top (or only if filtering by triaging) */}
          {currentTriaging && (filter === "all" || filter === "pending" || filter === "triaging") && (
            <TriagingPatientCard
              patient={currentTriaging}
              onComplete={handleTriagingComplete}
            />
          )}

          {/* Hide other patients when filtering by triaging only */}
          {filter !== "triaging" && filteredPatients.map((patient, index) => {
            const esi = esiConfig[patient.aiDecision.esi];
            const ArrivalIcon = arrivalModeIcons[patient.arrivalMode];
            const confidenceColor =
              patient.aiDecision.confidence >= 90
                ? "text-emerald-600"
                : patient.aiDecision.confidence >= 75
                ? "text-amber-600"
                : "text-red-600";

            return (
              <SwipeableCard
                key={patient.id}
                onSwipeRight={() => handleApprove(patient.id)}
                onSwipeLeft={() => handleManualReview(patient)}
                onTap={() => handlePatientTap(index)}
                disabled={patient.status === "approved"}
              >
                <div
                  className={cn(
                    "border rounded-lg p-3 transition-all",
                    patient.status === "in-review" && "border-sky-300 bg-sky-50/50",
                    patient.status === "approved" && "border-emerald-300 bg-emerald-50/50 opacity-60",
                    patient.status === "pending" && "border-slate-200 bg-background"
                  )}
                >
                  <div className="flex items-start gap-3">
                    {/* ESI Badge */}
                    <div
                      className={cn(
                        "w-11 h-11 rounded-lg flex flex-col items-center justify-center flex-shrink-0",
                        esi.color
                      )}
                    >
                      <span className="text-[11px] font-bold">{esi.label}</span>
                    </div>

                    {/* Patient Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="font-semibold text-sm">
                          {patient.name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {patient.age}{patient.gender}
                        </span>
                        {patient.status === "approved" && (
                          <Badge className="h-4 text-[9px] bg-emerald-100 text-emerald-700 border-emerald-200">
                            <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />
                            Approved
                          </Badge>
                        )}
                      </div>

                      <p className="text-xs text-slate-600 truncate mb-1.5">
                        {patient.chiefComplaint}
                      </p>

                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <ArrivalIcon className="w-3 h-3" />
                          {patient.arrivalMode}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {patient.arrivalTime}
                        </span>
                        <span className="flex items-center gap-1 text-amber-600 font-medium">
                          <Timer className="w-3 h-3" />
                          {patient.waitTime}
                        </span>
                      </div>
                    </div>

                    {/* AI Confidence - More Prominent */}
                    <div className="flex flex-col items-center flex-shrink-0">
                      <div className={cn("flex items-center gap-1", confidenceColor)}>
                        <Brain className="w-3.5 h-3.5" />
                        <span className="text-lg font-bold tabular-nums">
                          {patient.aiDecision.confidence}
                        </span>
                        <span className="text-[10px]">%</span>
                      </div>
                      <span className="text-[9px] text-muted-foreground">confidence</span>
                    </div>
                  </div>

                  {/* Critical indicators */}
                  {patient.aiDecision.esi <= 2 && patient.aiDecision.protocols.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-slate-100">
                      {patient.aiDecision.protocols.map((protocol, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="h-5 text-[10px] bg-amber-50 border-amber-200 text-amber-700"
                        >
                          {protocol}
                        </Badge>
                      ))}
                      <span className="ml-auto text-[10px] text-slate-400">
                        → {patient.aiDecision.bay}
                      </span>
                    </div>
                  )}
                </div>
              </SwipeableCard>
            );
          })}
        </div>

        {filteredPatients.length === 0 && !currentTriaging && (
          <div className="text-center py-12 text-muted-foreground">
            <Users className="w-8 h-8 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No patients match the current filter</p>
          </div>
        )}

        {filter === "triaging" && !currentTriaging && (
          <div className="text-center py-12 text-muted-foreground">
            <Brain className="w-8 h-8 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No patients currently being triaged</p>
          </div>
        )}
      </main>

      {/* Manual Review Modal */}
      <ManualReviewModal
        open={!!manualReviewPatient}
        onClose={() => setManualReviewPatient(null)}
        patientName={manualReviewPatient?.name || ""}
        onConfirmReview={handleConfirmManualReview}
      />
    </div>
  );
}
