"use client";

import { Vitals } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Heart,
  Activity,
  Wind,
  Thermometer,
  Droplets,
  Gauge,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";

interface VitalsGridProps {
  vitals: Vitals;
  className?: string;
}

const vitalConfig = {
  bp: { label: "BP", icon: Gauge },
  hr: { label: "HR", icon: Heart },
  spo2: { label: "SpO₂", icon: Droplets },
  temp: { label: "Temp", icon: Thermometer },
  rr: { label: "RR", icon: Wind },
  pain: { label: "Pain", icon: Activity },
};

const statusStyles = {
  critical: {
    bg: "bg-red-50",
    border: "border-red-200",
    text: "text-red-800",
    icon: "text-red-600",
  },
  warning: {
    bg: "bg-amber-50",
    border: "border-amber-200",
    text: "text-amber-800",
    icon: "text-amber-600",
  },
  normal: {
    bg: "bg-slate-50",
    border: "border-slate-200",
    text: "text-slate-700",
    icon: "text-slate-500",
  },
};

const TrendIcon = ({ trend }: { trend?: "up" | "down" | "stable" }) => {
  if (trend === "up") return <TrendingUp className="w-3 h-3 text-red-500" />;
  if (trend === "down") return <TrendingDown className="w-3 h-3 text-blue-500" />;
  return <Minus className="w-3 h-3 text-slate-300" />;
};

export function VitalsGrid({ vitals, className }: VitalsGridProps) {
  return (
    <div className={cn("grid grid-cols-3 md:grid-cols-6 gap-1.5", className)}>
      {(Object.keys(vitals) as Array<keyof Vitals>).map((key) => {
        const vital = vitals[key];
        const config = vitalConfig[key];
        const styles = statusStyles[vital.status];
        const Icon = config.icon;

        return (
          <div
            key={key}
            className={cn(
              "p-2 rounded border text-center",
              styles.bg,
              styles.border
            )}
          >
            <div className="flex items-center justify-center gap-1 mb-0.5">
              <Icon className={cn("w-3 h-3", styles.icon)} />
              <span className="text-[10px] font-medium text-muted-foreground">
                {config.label}
              </span>
              <TrendIcon trend={vital.trend} />
            </div>
            <div className={cn("text-sm font-semibold tabular-nums", styles.text)}>
              {vital.value}
            </div>
          </div>
        );
      })}
    </div>
  );
}
