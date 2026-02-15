"use client";

import { Badge } from "@/components/ui/badge";
import { AIDecision } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  MapPin,
  Users,
  FlaskConical,
  Scan,
  Syringe,
  Zap,
} from "lucide-react";

interface AIDecisionSummaryProps {
  decision: AIDecision;
  className?: string;
}

export function AIDecisionSummary({ decision, className }: AIDecisionSummaryProps) {
  const acuityColors = {
    critical: "bg-red-700 text-white",
    urgent: "bg-amber-600 text-white",
    minor: "bg-emerald-700 text-white",
  };

  const confidenceColor =
    decision.confidence >= 85
      ? "text-emerald-700"
      : decision.confidence >= 70
      ? "text-amber-600"
      : "text-red-700";

  return (
    <div className={cn("space-y-3.5", className)}>
      {/* Acuity + Confidence */}
      <div className="flex items-center gap-3">
        <div
          className={cn(
            "px-3 py-1.5 rounded font-semibold text-sm",
            acuityColors[decision.acuityColor]
          )}
        >
          ESI-{decision.esi} {decision.acuityLabel}
        </div>
        <div className="flex items-baseline gap-1">
          <span className={cn("text-xl font-semibold tabular-nums", confidenceColor)}>
            {decision.confidence}%
          </span>
          <span className="text-xs text-muted-foreground">confidence</span>
        </div>
      </div>

      {/* Bay + Specialists - 2 column with inline icon+label */}
      <div className="grid grid-cols-2 gap-2">
        <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
          <div className="flex items-center gap-1 text-[11px] text-muted-foreground uppercase tracking-wide mb-0.5">
            <MapPin className="w-3 h-3" />
            <span>Bay</span>
          </div>
          <div className="font-semibold text-sm">{decision.bay}</div>
        </div>
        <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
          <div className="flex items-center gap-1 text-[11px] text-muted-foreground uppercase tracking-wide mb-0.5">
            <Users className="w-3 h-3" />
            <span>Page</span>
          </div>
          <div className="font-semibold text-sm">{decision.specialists.join(", ")}</div>
        </div>
      </div>

      {/* Actions */}
      <div className="border border-slate-200 rounded overflow-hidden">
        <div className="px-2.5 py-1 bg-slate-50 border-b border-slate-200">
          <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Actions</span>
        </div>
        <div className="divide-y divide-slate-100">
        {/* Protocols */}
        {decision.protocols.length > 0 && (
          <div className="flex items-start gap-2 px-2.5 py-2.5 bg-amber-50/50">
            <Zap className="w-3.5 h-3.5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <span className="text-[11px] text-amber-700 font-medium block mb-1">Protocols</span>
              <div className="flex flex-wrap gap-1">
                {decision.protocols.map((protocol, i) => (
                  <Badge key={i} variant="outline" className="h-5 text-[11px] bg-amber-100 border-amber-300 text-amber-800 font-medium">
                    {protocol}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}
        <div className="flex items-start gap-2 px-2.5 py-2.5">
          <FlaskConical className="w-3.5 h-3.5 text-teal-600 mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-[11px] text-slate-500 font-medium block mb-1">Labs</span>
            <div className="flex flex-wrap gap-1">
              {decision.labs.map((lab, i) => (
                <Badge key={i} variant="outline" className="h-5 text-[11px] bg-teal-50 border-teal-200 text-teal-800">
                  {lab}
                </Badge>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-start gap-2 px-2.5 py-2.5 bg-slate-50/50">
          <Scan className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-[11px] text-slate-500 font-medium block mb-1">Imaging</span>
            <div className="flex flex-wrap gap-1">
              {decision.imaging.map((img, i) => (
                <Badge key={i} variant="outline" className="h-5 text-[11px] bg-slate-100 border-slate-300 text-slate-700">
                  {img}
                </Badge>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-start gap-2 px-2.5 py-2.5">
          <Syringe className="w-3.5 h-3.5 text-red-600 mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-[11px] text-slate-500 font-medium block mb-1">Interventions</span>
            <div className="flex flex-wrap gap-1">
              {decision.interventions.map((intervention, i) => (
                <Badge key={i} variant="outline" className="h-5 text-[11px] bg-red-50 border-red-200 text-red-800">
                  {intervention}
                </Badge>
              ))}
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}
