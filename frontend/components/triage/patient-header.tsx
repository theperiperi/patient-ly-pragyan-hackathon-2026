"use client";

import { Badge } from "@/components/ui/badge";
import { Patient } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Ambulance, Building, Clock } from "lucide-react";

interface PatientHeaderProps {
  patient: Patient;
  className?: string;
}

const arrivalModeIcons = {
  Ambulance: Ambulance,
  "Walk-in": Building,
  Referral: Building,
};

export function PatientHeader({ patient, className }: PatientHeaderProps) {
  const ArrivalIcon = arrivalModeIcons[patient.arrivalMode];

  return (
    <div className={cn("flex flex-wrap items-center justify-between gap-x-3 gap-y-1", className)}>
      {/* Name + ABHA - stays on one line, doesn't wrap */}
      <div className="flex items-center gap-2 min-w-0">
        <h1 className="text-lg font-semibold tracking-tight whitespace-nowrap">
          {patient.name}, {patient.age}{patient.gender}
        </h1>
        <span className="text-xs text-muted-foreground font-mono whitespace-nowrap">
          ••{patient.abha.slice(-4)}
        </span>
      </div>
      {/* Badges - wrap to next row if needed, left-aligned when wrapped */}
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Badge
          variant="outline"
          className={cn(
            "h-6 text-xs px-2 font-medium",
            patient.arrivalMode === "Ambulance" &&
              "bg-red-50 border-red-200 text-red-700"
          )}
        >
          <ArrivalIcon className="w-3 h-3 mr-1" />
          {patient.arrivalMode}
        </Badge>
        <span className="flex items-center gap-1.5 whitespace-nowrap">
          <Clock className="w-3.5 h-3.5" />
          {patient.arrivalTime}
        </span>
      </div>
    </div>
  );
}
