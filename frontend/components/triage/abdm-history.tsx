"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { ABDMData } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Database,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface ABDMHistoryProps {
  data: ABDMData;
  className?: string;
}

export function ABDMHistory({ data, className }: ABDMHistoryProps) {
  const [expanded, setExpanded] = useState(false);

  const totalRecords = data.encounters.length + data.conditions.length + data.medications.length;

  return (
    <div className={cn("border border-slate-200 rounded", className)}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-2 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-medium">ABDM Records</span>
          <Badge variant="secondary" className="h-5 text-[10px] bg-slate-100 text-slate-600">
            {totalRecords}
          </Badge>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {expanded && (
        <div className="px-2.5 pb-2.5 space-y-2 border-t border-slate-100 pt-2.5 text-xs">
          {/* Conditions */}
          <div>
            <span className="font-semibold text-slate-700">Conditions: </span>
            <span className="text-slate-600">
              {data.conditions.map((c) => c.name).join(", ")}
            </span>
          </div>

          {/* Medications */}
          <div>
            <span className="font-semibold text-slate-700">Medications: </span>
            <span className="text-slate-600">
              {data.medications.map((m) => m.name).join(", ")}
            </span>
          </div>

          {/* Allergies */}
          {data.allergies.length > 0 && (
            <div>
              <span className="font-semibold text-red-700">Allergies: </span>
              <span className="text-red-600">{data.allergies.join(", ")}</span>
            </div>
          )}

          {/* Encounters */}
          <div>
            <span className="font-semibold text-slate-700">Recent: </span>
            <span className="text-slate-600">
              {data.encounters.slice(0, 2).map((e) => `${e.date} - ${e.type}`).join("; ")}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
