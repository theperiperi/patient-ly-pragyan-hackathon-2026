"use client";

import { useState } from "react";
import { AIDecision, ESILevel } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import {
  Check,
  X,
  Plus,
  MapPin,
  Users,
  Zap,
  FlaskConical,
  Scan,
  Syringe,
} from "lucide-react";

interface ModifyModalProps {
  open: boolean;
  onClose: () => void;
  decision: AIDecision;
  onApproveModified: (modified: AIDecision) => void;
}

const esiOptions: { level: ESILevel; label: string; color: string }[] = [
  { level: 1, label: "Resuscitation", color: "bg-red-600 text-white border-red-600" },
  { level: 2, label: "Emergent", color: "bg-red-500 text-white border-red-500" },
  { level: 3, label: "Urgent", color: "bg-amber-500 text-white border-amber-500" },
  { level: 4, label: "Less Urgent", color: "bg-emerald-600 text-white border-emerald-600" },
  { level: 5, label: "Non-Urgent", color: "bg-emerald-500 text-white border-emerald-500" },
];

const bayOptions = [
  "Resus Bay 1",
  "Resus Bay 2",
  "Trauma Bay",
  "Cardiac Bay",
  "Fast Track",
  "Observation",
  "Waiting Area",
];

const specialistOptions = [
  "Cardiology (STAT)",
  "Interventional Cardiology",
  "Neurology",
  "Neurosurgery",
  "Trauma Surgery",
  "OB/GYN",
  "Anesthesia",
  "Internal Medicine",
  "Pediatrics",
  "Orthopedics",
];

const protocolOptions = [
  "STEMI Alert",
  "Stroke Alert",
  "Trauma Alert",
  "Sepsis Protocol",
  "Code Blue",
  "Massive Transfusion",
  "OB Emergency",
  "Hypothermia Protocol",
];

const commonLabs = [
  "Troponin",
  "CBC",
  "BMP",
  "CMP",
  "Coags",
  "Lactate",
  "BNP",
  "D-Dimer",
  "ABG",
  "Type & Screen",
  "Lipase",
  "LFTs",
  "UA",
];

const commonImaging = [
  "ECG",
  "Chest X-ray",
  "CT Head",
  "CT Chest",
  "CT Abdomen",
  "CTA",
  "Ultrasound",
  "Echo",
  "MRI",
];

const commonInterventions = [
  "IV Access x2",
  "O2 Therapy",
  "Cardiac Monitoring",
  "ASA 325mg",
  "Heparin",
  "Nitro SL",
  "Pain Management",
  "Fluids",
  "Foley",
  "NG Tube",
];

export function ModifyModal({
  open,
  onClose,
  decision,
  onApproveModified,
}: ModifyModalProps) {
  const [modified, setModified] = useState<AIDecision>({ ...decision });

  const handleEsiChange = (esi: ESILevel) => {
    const option = esiOptions.find((o) => o.level === esi)!;
    setModified({
      ...modified,
      esi,
      acuityLabel: option.label,
      acuityColor: esi <= 2 ? "critical" : esi === 3 ? "urgent" : "minor",
    });
  };

  const toggleItem = (
    field: "specialists" | "protocols" | "labs" | "imaging" | "interventions",
    item: string
  ) => {
    const current = modified[field];
    const updated = current.includes(item)
      ? current.filter((i) => i !== item)
      : [...current, item];
    setModified({ ...modified, [field]: updated });
  };

  const isChanged = (
    field: "esi" | "bay" | "specialists" | "protocols" | "labs" | "imaging" | "interventions"
  ) => {
    if (field === "esi" || field === "bay") {
      return modified[field] !== decision[field];
    }
    const orig = decision[field] as string[];
    const mod = modified[field] as string[];
    return JSON.stringify(orig.sort()) !== JSON.stringify(mod.sort());
  };

  const hasAnyChanges =
    isChanged("esi") ||
    isChanged("bay") ||
    isChanged("specialists") ||
    isChanged("protocols") ||
    isChanged("labs") ||
    isChanged("imaging") ||
    isChanged("interventions");

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="h-[85vh] overflow-y-auto px-5" showCloseButton={false}>
        <SheetHeader className="text-left pb-4 border-b">
          <SheetTitle className="flex items-center justify-between">
            <span>Modify AI Recommendation</span>
            <button
              onClick={onClose}
              className="p-1.5 rounded hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>
          </SheetTitle>
        </SheetHeader>

        <div className="py-5 space-y-6">
          {/* ESI Level */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-sm font-semibold">ESI Level</h3>
              {isChanged("esi") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {esiOptions.map((option) => (
                <button
                  key={option.level}
                  onClick={() => handleEsiChange(option.level)}
                  className={cn(
                    "px-3 py-1.5 rounded text-sm font-medium border-2 transition-all",
                    modified.esi === option.level
                      ? option.color
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  ESI-{option.level}
                </button>
              ))}
            </div>
          </section>

          {/* Bay Assignment */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-4 h-4 text-slate-500" />
              <h3 className="text-sm font-semibold">Bay Assignment</h3>
              {isChanged("bay") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {bayOptions.map((bay) => (
                <button
                  key={bay}
                  onClick={() => setModified({ ...modified, bay })}
                  className={cn(
                    "px-3 py-1.5 rounded text-sm border transition-all",
                    modified.bay === bay
                      ? "bg-slate-800 text-white border-slate-800"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  {bay}
                </button>
              ))}
            </div>
          </section>

          {/* Specialists */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-4 h-4 text-slate-500" />
              <h3 className="text-sm font-semibold">Page Specialists</h3>
              {isChanged("specialists") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {specialistOptions.map((spec) => (
                <button
                  key={spec}
                  onClick={() => toggleItem("specialists", spec)}
                  className={cn(
                    "px-3 py-1.5 rounded text-sm border transition-all flex items-center gap-1.5",
                    modified.specialists.includes(spec)
                      ? "bg-sky-100 text-sky-800 border-sky-300"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  {modified.specialists.includes(spec) && <Check className="w-3 h-3" />}
                  {spec}
                </button>
              ))}
            </div>
          </section>

          {/* Protocols */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-semibold">Protocols</h3>
              {isChanged("protocols") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {protocolOptions.map((protocol) => (
                <button
                  key={protocol}
                  onClick={() => toggleItem("protocols", protocol)}
                  className={cn(
                    "px-3 py-1.5 rounded text-sm border transition-all flex items-center gap-1.5",
                    modified.protocols.includes(protocol)
                      ? "bg-amber-100 text-amber-800 border-amber-300"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  {modified.protocols.includes(protocol) && <Check className="w-3 h-3" />}
                  {protocol}
                </button>
              ))}
            </div>
          </section>

          {/* Labs */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <FlaskConical className="w-4 h-4 text-teal-600" />
              <h3 className="text-sm font-semibold">Labs</h3>
              {isChanged("labs") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {commonLabs.map((lab) => (
                <button
                  key={lab}
                  onClick={() => toggleItem("labs", lab)}
                  className={cn(
                    "px-2.5 py-1 rounded text-xs border transition-all flex items-center gap-1",
                    modified.labs.includes(lab)
                      ? "bg-teal-100 text-teal-800 border-teal-300"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  {modified.labs.includes(lab) ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <Plus className="w-3 h-3" />
                  )}
                  {lab}
                </button>
              ))}
            </div>
          </section>

          {/* Imaging */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <Scan className="w-4 h-4 text-slate-500" />
              <h3 className="text-sm font-semibold">Imaging</h3>
              {isChanged("imaging") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {commonImaging.map((img) => (
                <button
                  key={img}
                  onClick={() => toggleItem("imaging", img)}
                  className={cn(
                    "px-2.5 py-1 rounded text-xs border transition-all flex items-center gap-1",
                    modified.imaging.includes(img)
                      ? "bg-slate-700 text-white border-slate-700"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  {modified.imaging.includes(img) ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <Plus className="w-3 h-3" />
                  )}
                  {img}
                </button>
              ))}
            </div>
          </section>

          {/* Interventions */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <Syringe className="w-4 h-4 text-red-600" />
              <h3 className="text-sm font-semibold">Interventions</h3>
              {isChanged("interventions") && (
                <Badge variant="outline" className="text-[10px] h-4 bg-amber-50 text-amber-700 border-amber-200">
                  Modified
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {commonInterventions.map((intervention) => (
                <button
                  key={intervention}
                  onClick={() => toggleItem("interventions", intervention)}
                  className={cn(
                    "px-2.5 py-1 rounded text-xs border transition-all flex items-center gap-1",
                    modified.interventions.includes(intervention)
                      ? "bg-red-100 text-red-800 border-red-300"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  {modified.interventions.includes(intervention) ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <Plus className="w-3 h-3" />
                  )}
                  {intervention}
                </button>
              ))}
            </div>
          </section>
        </div>

        {/* Sticky footer */}
        <div className="sticky bottom-0 bg-background border-t pt-4 pb-4 -mx-5 px-5">
          <button
            onClick={() => onApproveModified(modified)}
            disabled={!hasAnyChanges}
            className={cn(
              "w-full h-12 rounded-lg font-semibold text-sm transition-all",
              hasAnyChanges
                ? "bg-emerald-600 text-white hover:bg-emerald-700 active:scale-[0.98]"
                : "bg-slate-100 text-slate-400 cursor-not-allowed"
            )}
          >
            {hasAnyChanges ? "Approve Modified Plan" : "No Changes Made"}
          </button>
          <p className="text-center text-xs text-muted-foreground mt-2">
            Original AI recommendation will be overridden
          </p>
        </div>
      </SheetContent>
    </Sheet>
  );
}
