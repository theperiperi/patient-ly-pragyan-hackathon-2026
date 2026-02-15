"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { mockPatients } from "@/lib/mock-data";
import { Patient } from "@/lib/types";
import {
  Activity,
  Users,
  AlertTriangle,
  Clock,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Brain,
  Stethoscope,
  Heart,
  ChevronRight,
  ArrowLeft,
  Zap,
  Shield,
  Gauge,
  Radio,
  Waves,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ============================================================================
// DATA COMPUTATION
// ============================================================================

function computeStats(patients: Patient[]) {
  const stats = {
    total: patients.length,
    byESI: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 } as Record<number, number>,
    byAcuity: { critical: 0, urgent: 0, minor: 0 },
    byDepartment: {} as Record<string, number>,
    avgConfidence: 0,
    highRisk: 0,
    mediumRisk: 0,
    lowRisk: 0,
    avgTriageTime: 47,
    triaged24h: 24,
  };

  let totalConfidence = 0;

  patients.forEach((p) => {
    stats.byESI[p.aiDecision.esi]++;
    stats.byAcuity[p.aiDecision.acuityColor]++;
    p.aiDecision.specialists.forEach((spec) => {
      stats.byDepartment[spec] = (stats.byDepartment[spec] || 0) + 1;
    });
    totalConfidence += p.aiDecision.confidence;
    if (p.aiDecision.esi <= 2) stats.highRisk++;
    else if (p.aiDecision.esi === 3) stats.mediumRisk++;
    else stats.lowRisk++;
  });

  stats.avgConfidence = Math.round(totalConfidence / patients.length);
  return stats;
}

// ============================================================================
// ANIMATED COMPONENTS
// ============================================================================

// Animated number counter with smooth easing
function AnimatedNumber({
  value,
  suffix = "",
  decimals = 0,
  duration = 1500
}: {
  value: number;
  suffix?: string;
  decimals?: number;
  duration?: number;
}) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const steps = 60;
    const increment = value / steps;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      // Ease out cubic
      const progress = 1 - Math.pow(1 - step / steps, 3);
      setCurrent(Number((value * progress).toFixed(decimals)));
      if (step >= steps) clearInterval(timer);
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value, decimals, duration]);

  return (
    <span className="font-mono tabular-nums">
      {decimals > 0 ? current.toFixed(decimals) : current}
      {suffix}
    </span>
  );
}

// Live pulse indicator with glow
function PulseIndicator({ color = "emerald", size = "md" }: { color?: string; size?: "sm" | "md" | "lg" }) {
  const sizeClasses = {
    sm: "h-1.5 w-1.5",
    md: "h-2.5 w-2.5",
    lg: "h-3 w-3",
  };

  const colorClasses: Record<string, string> = {
    emerald: "bg-emerald-500 shadow-emerald-500/50",
    red: "bg-red-500 shadow-red-500/50",
    amber: "bg-amber-500 shadow-amber-500/50",
    cyan: "bg-cyan-500 shadow-cyan-500/50",
  };

  return (
    <span className="relative flex">
      <span className={cn(
        "absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping",
        colorClasses[color]?.split(" ")[0]
      )} />
      <span className={cn(
        "relative inline-flex rounded-full shadow-lg",
        sizeClasses[size],
        colorClasses[color]
      )} />
    </span>
  );
}

// Heartbeat line animation
function HeartbeatLine() {
  return (
    <div className="absolute inset-0 overflow-hidden opacity-20">
      <svg
        className="absolute top-1/2 -translate-y-1/2 w-full h-12 animate-pulse-line"
        viewBox="0 0 1200 50"
        preserveAspectRatio="none"
      >
        <path
          d="M0,25 L200,25 L220,25 L230,10 L240,40 L250,5 L260,45 L270,20 L280,30 L290,25 L400,25 L1200,25"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-cyan-400"
        />
      </svg>
    </div>
  );
}

// ============================================================================
// METRIC CARDS
// ============================================================================

function MetricCard({
  label,
  value,
  suffix = "",
  subValue,
  trend,
  trendValue,
  icon: Icon,
  accentColor = "cyan",
  delay = 0,
  glowing = false,
}: {
  label: string;
  value: number;
  suffix?: string;
  subValue?: string;
  trend?: "up" | "down";
  trendValue?: string;
  icon: React.ElementType;
  accentColor?: "cyan" | "red" | "amber" | "emerald" | "violet";
  delay?: number;
  glowing?: boolean;
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const accentClasses: Record<string, { border: string; icon: string; glow: string }> = {
    cyan: {
      border: "border-cyan-500/30",
      icon: "text-cyan-400",
      glow: "shadow-cyan-500/20",
    },
    red: {
      border: "border-red-500/30",
      icon: "text-red-400",
      glow: "shadow-red-500/20",
    },
    amber: {
      border: "border-amber-500/30",
      icon: "text-amber-400",
      glow: "shadow-amber-500/20",
    },
    emerald: {
      border: "border-emerald-500/30",
      icon: "text-emerald-400",
      glow: "shadow-emerald-500/20",
    },
    violet: {
      border: "border-violet-500/30",
      icon: "text-violet-400",
      glow: "shadow-violet-500/20",
    },
  };

  const accent = accentClasses[accentColor];

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border bg-slate-900/80 backdrop-blur-sm p-4 transition-all duration-700",
        accent.border,
        glowing && `shadow-lg ${accent.glow}`,
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
      )}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />

      {/* Scanline effect */}
      <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] pointer-events-none opacity-30" />

      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
            {label}
          </p>
          <Icon className={cn("h-4 w-4", accent.icon)} />
        </div>

        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-white">
            {visible ? <AnimatedNumber value={value} suffix={suffix} /> : "0"}
          </span>
        </div>

        {subValue && (
          <p className="mt-1 text-xs text-slate-500">{subValue}</p>
        )}

        {trend && trendValue && (
          <div className="flex items-center gap-1.5 mt-3 pt-3 border-t border-slate-800">
            <div className={cn(
              "flex items-center gap-1 text-xs font-medium",
              trend === "up" ? "text-emerald-400" : "text-red-400"
            )}>
              {trend === "up" ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {trendValue}
            </div>
            <span className="text-xs text-slate-600">vs last hour</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// ESI SEVERITY DISPLAY
// ============================================================================

function ESISeverityGrid({ byESI, total }: { byESI: Record<number, number>; total: number }) {
  const esiConfig = [
    { level: 1, label: "Resuscitation", color: "bg-red-500", textColor: "text-red-400", borderColor: "border-red-500/40", glowColor: "shadow-red-500/30" },
    { level: 2, label: "Emergent", color: "bg-orange-500", textColor: "text-orange-400", borderColor: "border-orange-500/40", glowColor: "shadow-orange-500/30" },
    { level: 3, label: "Urgent", color: "bg-amber-500", textColor: "text-amber-400", borderColor: "border-amber-500/40", glowColor: "shadow-amber-500/30" },
    { level: 4, label: "Less Urgent", color: "bg-lime-500", textColor: "text-lime-400", borderColor: "border-lime-500/40", glowColor: "shadow-lime-500/20" },
    { level: 5, label: "Non-Urgent", color: "bg-emerald-500", textColor: "text-emerald-400", borderColor: "border-emerald-500/40", glowColor: "shadow-emerald-500/20" },
  ];

  return (
    <div className="space-y-3">
      {esiConfig.map(({ level, label, color, textColor, borderColor, glowColor }) => {
        const count = byESI[level];
        const pct = total > 0 ? (count / total) * 100 : 0;
        const isHighPriority = level <= 2;

        return (
          <div
            key={level}
            className={cn(
              "relative rounded-lg border p-3 transition-all duration-300",
              borderColor,
              isHighPriority && count > 0 && `shadow-lg ${glowColor}`,
              "bg-slate-900/60 hover:bg-slate-900/80"
            )}
          >
            {/* Progress bar background */}
            <div className="absolute inset-0 rounded-lg overflow-hidden">
              <div
                className={cn("h-full opacity-10 transition-all duration-1000", color)}
                style={{ width: `${pct}%` }}
              />
            </div>

            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "flex items-center justify-center h-8 w-8 rounded-md font-mono font-bold text-sm",
                  color,
                  "text-white"
                )}>
                  {level}
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-200">{label}</p>
                  <p className="text-xs text-slate-500">ESI Level {level}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className={cn("text-2xl font-bold font-mono", textColor)}>
                    {count}
                  </p>
                  <p className="text-xs text-slate-500">{pct.toFixed(1)}%</p>
                </div>

                {isHighPriority && count > 0 && (
                  <PulseIndicator color={level === 1 ? "red" : "amber"} size="sm" />
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ============================================================================
// DEPARTMENT WORKLOAD
// ============================================================================

function DepartmentWorkload({ data }: { data: Record<string, number> }) {
  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = sorted[0]?.[1] || 1;
  const total = Object.values(data).reduce((a, b) => a + b, 0);

  const deptIcons: Record<string, React.ElementType> = {
    Cardiology: Heart,
    "Emergency Medicine": Zap,
    "Internal Medicine": Stethoscope,
    Neurology: Brain,
    Orthopedics: Activity,
    default: Stethoscope,
  };

  return (
    <div className="space-y-2">
      {sorted.slice(0, 7).map(([dept, count], idx) => {
        const Icon = deptIcons[dept] || deptIcons.default;
        const pct = (count / max) * 100;
        const share = ((count / total) * 100).toFixed(0);

        return (
          <div
            key={dept}
            className="group relative rounded-md border border-slate-800 bg-slate-900/40 p-3 hover:border-slate-700 hover:bg-slate-900/60 transition-all duration-200"
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-slate-500 group-hover:text-cyan-400 transition-colors" />
                <span className="text-sm text-slate-300 group-hover:text-white transition-colors">
                  {dept}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-500">{share}%</span>
                <span className="font-mono font-semibold text-cyan-400">{count}</span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="h-1 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-teal-500 rounded-full transition-all duration-700"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ============================================================================
// RISK DISTRIBUTION
// ============================================================================

function RiskGauge({ high, medium, low, total }: { high: number; medium: number; low: number; total: number }) {
  const highPct = (high / total) * 100;
  const medPct = (medium / total) * 100;
  const lowPct = (low / total) * 100;

  return (
    <div className="space-y-4">
      {/* Main gauge */}
      <div className="relative h-3 rounded-full bg-slate-800 overflow-hidden">
        <div className="absolute inset-0 flex">
          <div
            className="h-full bg-gradient-to-r from-red-600 to-red-500 transition-all duration-1000"
            style={{ width: `${highPct}%` }}
          />
          <div
            className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-1000"
            style={{ width: `${medPct}%` }}
          />
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-1000"
            style={{ width: `${lowPct}%` }}
          />
        </div>
        {/* Glow overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent pointer-events-none" />
      </div>

      {/* Legend */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "High Risk", value: high, pct: highPct, color: "red", icon: AlertTriangle },
          { label: "Medium", value: medium, pct: medPct, color: "amber", icon: Clock },
          { label: "Low Risk", value: low, pct: lowPct, color: "emerald", icon: Shield },
        ].map(({ label, value, pct, color, icon: Icon }) => (
          <div key={label} className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <div className={cn("h-2 w-2 rounded-full", `bg-${color}-500`)} />
              <span className="text-xs text-slate-400">{label}</span>
            </div>
            <div className={cn("text-2xl font-bold font-mono", `text-${color}-400`)}>
              {value}
            </div>
            <div className="text-xs text-slate-600">{pct.toFixed(1)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// RECENT ACTIVITY TABLE
// ============================================================================

function ActivityTable({ patients }: { patients: Patient[] }) {
  const recent = patients.slice(0, 10);

  const esiColors: Record<number, string> = {
    1: "bg-red-500 shadow-red-500/50",
    2: "bg-orange-500 shadow-orange-500/40",
    3: "bg-amber-500 shadow-amber-500/30",
    4: "bg-lime-500",
    5: "bg-emerald-500",
  };

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800">
      {/* Table header */}
      <div className="grid grid-cols-12 gap-2 px-4 py-3 bg-slate-900/80 border-b border-slate-800 text-[11px] font-medium uppercase tracking-wider text-slate-500">
        <div className="col-span-3">Patient</div>
        <div className="col-span-4">Chief Complaint</div>
        <div className="col-span-1 text-center">ESI</div>
        <div className="col-span-2 text-center">Confidence</div>
        <div className="col-span-2 text-right">Time</div>
      </div>

      {/* Table body */}
      <div className="divide-y divide-slate-800/50">
        {recent.map((patient, idx) => (
          <div
            key={patient.id}
            className="grid grid-cols-12 gap-2 px-4 py-3 hover:bg-slate-800/30 transition-colors group"
            style={{ animationDelay: `${idx * 30}ms` }}
          >
            <div className="col-span-3">
              <p className="text-sm font-medium text-slate-200 group-hover:text-white transition-colors truncate">
                {patient.name}
              </p>
              <p className="text-xs text-slate-600 font-mono">
                {patient.age}{patient.gender} • {patient.abha.slice(0, 11)}
              </p>
            </div>

            <div className="col-span-4 flex items-center">
              <p className="text-sm text-slate-400 truncate">
                {patient.chiefComplaint}
              </p>
            </div>

            <div className="col-span-1 flex items-center justify-center">
              <span
                className={cn(
                  "inline-flex h-6 w-6 items-center justify-center rounded text-[11px] font-bold text-white shadow-lg",
                  esiColors[patient.aiDecision.esi]
                )}
              >
                {patient.aiDecision.esi}
              </span>
            </div>

            <div className="col-span-2 flex items-center justify-center">
              <div className="flex items-center gap-2">
                <div className="w-12 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all duration-500",
                      patient.aiDecision.confidence >= 85
                        ? "bg-emerald-500"
                        : patient.aiDecision.confidence >= 70
                        ? "bg-amber-500"
                        : "bg-red-500"
                    )}
                    style={{ width: `${patient.aiDecision.confidence}%` }}
                  />
                </div>
                <span className={cn(
                  "text-sm font-mono font-semibold",
                  patient.aiDecision.confidence >= 85
                    ? "text-emerald-400"
                    : patient.aiDecision.confidence >= 70
                    ? "text-amber-400"
                    : "text-red-400"
                )}>
                  {patient.aiDecision.confidence}%
                </span>
              </div>
            </div>

            <div className="col-span-2 flex items-center justify-end">
              <span className="text-xs text-slate-500 font-mono">
                {patient.arrivalTime}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// MAIN DASHBOARD
// ============================================================================

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const stats = useMemo(() => computeStats(mockPatients), []);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    setMounted(true);
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0e14] text-slate-100">
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(14,165,233,0.08),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(16,185,129,0.05),transparent_50%)]" />
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: "40px 40px",
          }}
        />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-900/80 backdrop-blur-xl">
        <div className="relative max-w-[1600px] mx-auto px-6 py-4">
          <HeartbeatLine />

          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="p-2 -ml-2 rounded-lg hover:bg-slate-800 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-slate-400" />
              </Link>

              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 shadow-lg shadow-cyan-500/20">
                  <Gauge className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-white">Command Center</h1>
                  <p className="text-xs text-slate-500">Patient.ly Analytics</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-6">
              {/* Live indicator */}
              <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
                <PulseIndicator color="emerald" />
                <span className="text-sm text-slate-400">System Online</span>
                <div className="h-4 w-px bg-slate-700" />
                <span className="font-mono text-sm text-emerald-400">
                  {currentTime.toLocaleTimeString("en-US", { hour12: false })}
                </span>
              </div>

              <Link
                href="/queue"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-600 text-white text-sm font-semibold hover:from-cyan-400 hover:to-teal-500 transition-all shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30"
              >
                <Radio className="h-4 w-4" />
                Open Queue
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="relative max-w-[1600px] mx-auto px-6 py-6 space-y-6">
        {/* Top Metrics Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Patients"
            value={stats.total}
            subValue="In system today"
            icon={Users}
            trend="up"
            trendValue="+12%"
            accentColor="cyan"
            delay={0}
          />
          <MetricCard
            label="High Risk (ESI 1-2)"
            value={stats.highRisk}
            subValue="Requires immediate care"
            icon={AlertTriangle}
            trend="down"
            trendValue="-3%"
            accentColor="red"
            delay={100}
            glowing={stats.highRisk > 0}
          />
          <MetricCard
            label="AI Confidence"
            value={stats.avgConfidence}
            suffix="%"
            subValue="Average accuracy"
            icon={Brain}
            trend="up"
            trendValue="+2.1%"
            accentColor="violet"
            delay={200}
          />
          <MetricCard
            label="Avg. Triage Time"
            value={stats.avgTriageTime}
            suffix="s"
            subValue="Arrival to decision"
            icon={Zap}
            trend="down"
            trendValue="-12s"
            accentColor="emerald"
            delay={300}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - ESI Distribution */}
          <div className="lg:col-span-1 space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Waves className="h-4 w-4 text-cyan-400" />
                  <h2 className="font-semibold text-white">ESI Distribution</h2>
                </div>
                <span className="text-xs font-mono text-slate-500">
                  {stats.total} total
                </span>
              </div>
              <div className="p-5">
                <ESISeverityGrid byESI={stats.byESI} total={stats.total} />
              </div>
            </div>

            {/* Risk Gauge */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-800 flex items-center gap-2">
                <Shield className="h-4 w-4 text-cyan-400" />
                <h2 className="font-semibold text-white">Risk Overview</h2>
              </div>
              <div className="p-5">
                <RiskGauge
                  high={stats.highRisk}
                  medium={stats.mediumRisk}
                  low={stats.lowRisk}
                  total={stats.total}
                />
              </div>
            </div>
          </div>

          {/* Center/Right - Department & Activity */}
          <div className="lg:col-span-2 space-y-6">
            {/* Department Workload */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Stethoscope className="h-4 w-4 text-cyan-400" />
                  <h2 className="font-semibold text-white">Department Workload</h2>
                </div>
                <span className="text-xs text-slate-500">
                  {Object.keys(stats.byDepartment).length} departments
                </span>
              </div>
              <div className="p-5">
                <DepartmentWorkload data={stats.byDepartment} />
              </div>
            </div>

            {/* Recent Activity */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-cyan-400" />
                  <h2 className="font-semibold text-white">Recent Triage Activity</h2>
                </div>
                <Link
                  href="/queue"
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 transition-colors"
                >
                  View all
                  <ChevronRight className="h-3 w-3" />
                </Link>
              </div>
              <ActivityTable patients={mockPatients} />
            </div>
          </div>
        </div>

        {/* Footer Stats Bar */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-red-500/10 flex items-center justify-center">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Critical</p>
                  <p className="text-lg font-bold font-mono text-red-400">{stats.byAcuity.critical}</p>
                </div>
              </div>
              <div className="h-8 w-px bg-slate-800" />
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <Clock className="h-4 w-4 text-amber-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Urgent</p>
                  <p className="text-lg font-bold font-mono text-amber-400">{stats.byAcuity.urgent}</p>
                </div>
              </div>
              <div className="h-8 w-px bg-slate-800" />
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <Shield className="h-4 w-4 text-emerald-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Minor</p>
                  <p className="text-lg font-bold font-mono text-emerald-400">{stats.byAcuity.minor}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span>Last updated: just now</span>
              <PulseIndicator color="cyan" size="sm" />
            </div>
          </div>
        </div>
      </main>

      {/* Custom styles for animations */}
      <style jsx global>{`
        @keyframes pulse-line {
          0%, 100% { opacity: 0.2; transform: translateX(-100%); }
          50% { opacity: 0.4; transform: translateX(0%); }
        }
        .animate-pulse-line {
          animation: pulse-line 4s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
