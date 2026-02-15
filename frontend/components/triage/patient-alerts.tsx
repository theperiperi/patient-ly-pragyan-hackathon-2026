"use client";

import { Alert } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ShieldAlert } from "lucide-react";

interface PatientAlertsProps {
  alerts: Alert[];
  className?: string;
}

const severityIndicator = {
  critical: "bg-red-500",
  warning: "bg-amber-400",
  info: "bg-slate-300",
};

const severityText = {
  critical: "text-red-700 font-semibold",
  warning: "text-slate-700",
  info: "text-slate-600",
};

export function PatientAlerts({ alerts, className }: PatientAlertsProps) {
  // Sort alerts: critical first, then warning, then info
  const sortedAlerts = [...alerts].sort((a, b) => {
    const order = { critical: 0, warning: 1, info: 2 };
    return order[a.type] - order[b.type];
  });

  const criticalCount = alerts.filter(a => a.type === "critical").length;
  const warningCount = alerts.filter(a => a.type === "warning").length;

  return (
    <div className={cn("border border-slate-200 rounded", className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-2.5 py-1 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">
            Clinical Alerts
          </span>
        </div>
        <div className="flex items-center gap-2 text-[10px]">
          {criticalCount > 0 && (
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
              <span className="text-red-700 font-medium">{criticalCount} critical</span>
            </span>
          )}
          {warningCount > 0 && (
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span className="text-amber-700 font-medium">{warningCount} warning</span>
            </span>
          )}
        </div>
      </div>

      {/* Alert rows */}
      <div className="divide-y divide-slate-100">
        {sortedAlerts.map((alert, index) => (
          <div
            key={index}
            className="flex items-start gap-2 px-2.5 py-2 text-xs"
          >
            <span
              className={cn(
                "w-1 h-1 rounded-full mt-1.5 flex-shrink-0",
                severityIndicator[alert.type]
              )}
            />
            <p className={cn("leading-relaxed", severityText[alert.type])}>
              {alert.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
