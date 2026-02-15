"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { X, ClipboardList, Clock, AlertTriangle, Stethoscope } from "lucide-react";

interface ManualReviewModalProps {
  open: boolean;
  onClose: () => void;
  patientName: string;
  onConfirmReview: (reason: string, priority: "urgent" | "standard") => void;
}

const reviewReasons = [
  {
    id: "uncertain-diagnosis",
    icon: AlertTriangle,
    label: "Uncertain Diagnosis",
    description: "Need additional assessment to confirm diagnosis",
  },
  {
    id: "complex-history",
    icon: ClipboardList,
    label: "Complex Medical History",
    description: "Patient history requires careful review",
  },
  {
    id: "physical-exam",
    icon: Stethoscope,
    label: "Need Physical Exam",
    description: "Want to examine patient before disposition",
  },
  {
    id: "wait-results",
    icon: Clock,
    label: "Awaiting Results",
    description: "Need lab/imaging results before decision",
  },
];

export function ManualReviewModal({
  open,
  onClose,
  patientName,
  onConfirmReview,
}: ManualReviewModalProps) {
  const [selectedReason, setSelectedReason] = useState<string | null>(null);
  const [priority, setPriority] = useState<"urgent" | "standard">("standard");
  const [notes, setNotes] = useState("");

  const handleConfirm = () => {
    if (!selectedReason) return;
    const reason = reviewReasons.find((r) => r.id === selectedReason);
    const fullReason = notes ? `${reason?.label}: ${notes}` : reason?.label || "";
    onConfirmReview(fullReason, priority);
  };

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="h-auto max-h-[80vh] px-5" showCloseButton={false}>
        <SheetHeader className="text-left pb-4 border-b">
          <SheetTitle className="flex items-center justify-between">
            <span>Manual Review</span>
            <button
              onClick={onClose}
              className="p-1.5 rounded hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>
          </SheetTitle>
        </SheetHeader>

        <div className="py-5 space-y-5">
          <p className="text-sm text-muted-foreground">
            Flag <span className="font-medium text-foreground">{patientName}</span> for manual physician review instead of approving AI recommendation.
          </p>

          {/* Reason Selection */}
          <section>
            <h3 className="text-sm font-semibold mb-3">Reason for Review</h3>
            <div className="space-y-2">
              {reviewReasons.map((reason) => {
                const Icon = reason.icon;
                return (
                  <button
                    key={reason.id}
                    onClick={() => setSelectedReason(reason.id)}
                    className={cn(
                      "w-full flex items-start gap-3 p-3 rounded-lg border text-left transition-all",
                      selectedReason === reason.id
                        ? "border-slate-800 bg-slate-50"
                        : "border-slate-200 hover:border-slate-300"
                    )}
                  >
                    <div
                      className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                        selectedReason === reason.id
                          ? "bg-slate-800 text-white"
                          : "bg-slate-100 text-slate-500"
                      )}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{reason.label}</p>
                      <p className="text-xs text-muted-foreground">
                        {reason.description}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>

          {/* Priority */}
          <section>
            <h3 className="text-sm font-semibold mb-3">Review Priority</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setPriority("urgent")}
                className={cn(
                  "flex-1 py-2.5 rounded-lg border text-sm font-medium transition-all",
                  priority === "urgent"
                    ? "border-red-500 bg-red-50 text-red-700"
                    : "border-slate-200 text-slate-600 hover:border-slate-300"
                )}
              >
                Urgent
              </button>
              <button
                onClick={() => setPriority("standard")}
                className={cn(
                  "flex-1 py-2.5 rounded-lg border text-sm font-medium transition-all",
                  priority === "standard"
                    ? "border-slate-800 bg-slate-800 text-white"
                    : "border-slate-200 text-slate-600 hover:border-slate-300"
                )}
              >
                Standard
              </button>
            </div>
          </section>

          {/* Notes */}
          <section>
            <h3 className="text-sm font-semibold mb-3">Additional Notes <span className="font-normal text-muted-foreground">(optional)</span></h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any specific concerns or observations..."
              className="w-full h-20 px-3 py-2 rounded-lg border border-slate-200 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-slate-200"
            />
          </section>
        </div>

        {/* Footer */}
        <div className="border-t pt-4 pb-4 -mx-5 px-5">
          <button
            onClick={handleConfirm}
            disabled={!selectedReason}
            className={cn(
              "w-full h-12 rounded-lg font-semibold text-sm transition-all",
              selectedReason
                ? "bg-slate-800 text-white hover:bg-slate-900 active:scale-[0.98]"
                : "bg-slate-100 text-slate-400 cursor-not-allowed"
            )}
          >
            Flag for Manual Review
          </button>
          <p className="text-center text-xs text-muted-foreground mt-2">
            Patient will be added to physician review queue
          </p>
        </div>
      </SheetContent>
    </Sheet>
  );
}
