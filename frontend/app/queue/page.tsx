"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { mockPatients } from "@/lib/mock-data";
import { Patient } from "@/lib/types";
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
} from "lucide-react";

type FilterType = "all" | "critical" | "pending" | "approved";
type SortType = "acuity" | "arrival" | "wait";

interface QueuePatient extends Patient {
  status: "pending" | "in-review" | "approved";
  waitTime: string;
}

// Extend mock patients with queue-specific data
const queuePatients: QueuePatient[] = mockPatients.map((p, i) => ({
  ...p,
  status: i === 0 ? "in-review" : "pending",
  waitTime: i === 0 ? "12m" : i === 1 ? "8m" : "3m",
}));

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

  const stats = {
    total: patients.length,
    critical: patients.filter((p) => p.aiDecision.esi <= 2).length,
    pending: patients.filter((p) => p.status === "pending").length,
    approved: patients.filter((p) => p.status === "approved").length,
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
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <div className="flex gap-1">
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
          {filteredPatients.map((patient, index) => {
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

        {filteredPatients.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            <Users className="w-8 h-8 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No patients match the current filter</p>
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
