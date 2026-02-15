"use client";

import { useState } from "react";
import { SBARHandoff as SBARType } from "@/lib/types";
import { cn } from "@/lib/utils";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";

interface SBARHandoffProps {
  sbar: SBARType;
  className?: string;
}

const sbarSections = [
  { key: "situation" as const, label: "S", fullLabel: "Situation", color: "bg-rose-100 text-rose-700 border-rose-200" },
  { key: "background" as const, label: "B", fullLabel: "Background", color: "bg-amber-100 text-amber-700 border-amber-200" },
  { key: "assessment" as const, label: "A", fullLabel: "Assessment", color: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  { key: "recommendation" as const, label: "R", fullLabel: "Recommendation", color: "bg-sky-100 text-sky-700 border-sky-200" },
];

export function SBARHandoff({ sbar, className }: SBARHandoffProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={cn("border border-slate-200 rounded", className)}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-2 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-medium">SBAR Handoff</span>
          <div className="flex gap-0.5">
            {sbarSections.map((s) => (
              <span
                key={s.key}
                className={cn(
                  "w-5 h-5 rounded text-[10px] font-semibold flex items-center justify-center border",
                  s.color
                )}
              >
                {s.label}
              </span>
            ))}
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {expanded && (
        <div className="px-2.5 pb-2.5 space-y-2 border-t border-slate-100 pt-2.5">
          {sbarSections.map((section) => (
            <div key={section.key} className="flex items-start gap-2 text-xs">
              <span
                className={cn(
                  "w-5 h-5 rounded text-[10px] font-semibold flex items-center justify-center border flex-shrink-0 mt-0.5",
                  section.color
                )}
              >
                {section.label}
              </span>
              <div>
                <span className="font-semibold text-slate-700">
                  {section.fullLabel}:
                </span>{" "}
                <span className="text-slate-600">{sbar[section.key]}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
