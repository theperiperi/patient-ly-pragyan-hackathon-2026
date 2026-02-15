"use client";

import { useState, useEffect } from "react";
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
  Pill,
  Thermometer,
  ChevronRight,
  BarChart3,
  PieChart,
  ArrowLeft,
  CheckCircle2,
  Timer,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Compute dashboard statistics from patient data
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
  };

  let totalConfidence = 0;

  patients.forEach((p) => {
    // ESI distribution
    stats.byESI[p.aiDecision.esi]++;

    // Acuity distribution
    stats.byAcuity[p.aiDecision.acuityColor]++;

    // Department/Specialist distribution
    p.aiDecision.specialists.forEach((spec) => {
      stats.byDepartment[spec] = (stats.byDepartment[spec] || 0) + 1;
    });

    // Confidence
    totalConfidence += p.aiDecision.confidence;

    // Risk levels (ESI 1-2 = High, 3 = Medium, 4-5 = Low)
    if (p.aiDecision.esi <= 2) stats.highRisk++;
    else if (p.aiDecision.esi === 3) stats.mediumRisk++;
    else stats.lowRisk++;
  });

  stats.avgConfidence = Math.round(totalConfidence / patients.length);

  return stats;
}

// Summary card component
function SummaryCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendValue,
  color = "teal",
}: {
  title: string;
  value: React.ReactNode;
  subtitle?: string;
  icon: React.ElementType;
  trend?: "up" | "down";
  trendValue?: string;
  color?: "teal" | "red" | "amber" | "emerald" | "violet";
}) {
  const colorClasses = {
    teal: "bg-teal-50 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400",
    red: "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400",
    amber: "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400",
    emerald: "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400",
    violet: "bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400",
  };

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={cn("p-3 rounded-xl", colorClasses[color])}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      {trend && trendValue && (
        <div className="flex items-center gap-1 mt-3 text-xs">
          {trend === "up" ? (
            <TrendingUp className="h-3 w-3 text-emerald-500" />
          ) : (
            <TrendingDown className="h-3 w-3 text-red-500" />
          )}
          <span className={trend === "up" ? "text-emerald-600" : "text-red-600"}>
            {trendValue}
          </span>
          <span className="text-slate-400">vs last hour</span>
        </div>
      )}
    </div>
  );
}

// Risk distribution bar
function RiskDistributionBar({
  high,
  medium,
  low,
  total,
}: {
  high: number;
  medium: number;
  low: number;
  total: number;
}) {
  const highPct = (high / total) * 100;
  const medPct = (medium / total) * 100;
  const lowPct = (low / total) * 100;

  return (
    <div className="space-y-3">
      <div className="flex h-4 rounded-full overflow-hidden bg-slate-100 dark:bg-slate-800">
        <div
          className="bg-red-500 transition-all duration-500"
          style={{ width: `${highPct}%` }}
        />
        <div
          className="bg-amber-500 transition-all duration-500"
          style={{ width: `${medPct}%` }}
        />
        <div
          className="bg-emerald-500 transition-all duration-500"
          style={{ width: `${lowPct}%` }}
        />
      </div>
      <div className="flex justify-between text-sm">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-red-500" />
          <span className="text-slate-600 dark:text-slate-400">High Risk</span>
          <span className="font-semibold text-slate-900 dark:text-slate-100">{high}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-amber-500" />
          <span className="text-slate-600 dark:text-slate-400">Medium</span>
          <span className="font-semibold text-slate-900 dark:text-slate-100">{medium}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-emerald-500" />
          <span className="text-slate-600 dark:text-slate-400">Low Risk</span>
          <span className="font-semibold text-slate-900 dark:text-slate-100">{low}</span>
        </div>
      </div>
    </div>
  );
}

// ESI Level donut chart (CSS-based)
function ESIDonutChart({ byESI, total }: { byESI: Record<number, number>; total: number }) {
  const esiColors = {
    1: "#dc2626", // red-600
    2: "#ea580c", // orange-600
    3: "#d97706", // amber-600
    4: "#65a30d", // lime-600
    5: "#16a34a", // green-600
  };

  const esiLabels = {
    1: "Resuscitation",
    2: "Emergent",
    3: "Urgent",
    4: "Less Urgent",
    5: "Non-Urgent",
  };

  // Calculate cumulative percentages for conic gradient
  let cumulative = 0;
  const gradientStops: string[] = [];

  [1, 2, 3, 4, 5].forEach((esi) => {
    const pct = (byESI[esi] / total) * 100;
    if (pct > 0) {
      gradientStops.push(`${esiColors[esi as keyof typeof esiColors]} ${cumulative}% ${cumulative + pct}%`);
      cumulative += pct;
    }
  });

  return (
    <div className="flex items-center gap-8">
      {/* Donut */}
      <div className="relative">
        <div
          className="h-40 w-40 rounded-full"
          style={{
            background: `conic-gradient(${gradientStops.join(", ")})`,
          }}
        />
        <div className="absolute inset-4 rounded-full bg-white dark:bg-slate-900 flex items-center justify-center">
          <div className="text-center">
            <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{total}</p>
            <p className="text-xs text-slate-500">Patients</p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((esi) => (
          <div key={esi} className="flex items-center gap-2 text-sm">
            <div
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: esiColors[esi as keyof typeof esiColors] }}
            />
            <span className="text-slate-600 dark:text-slate-400 w-24">
              ESI-{esi}
            </span>
            <span className="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
              {byESI[esi]}
            </span>
            <span className="text-slate-400 text-xs">
              ({Math.round((byESI[esi] / total) * 100)}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Department bar chart
function DepartmentBarChart({ data }: { data: Record<string, number> }) {
  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = sorted[0]?.[1] || 1;

  const deptIcons: Record<string, React.ElementType> = {
    Cardiology: Heart,
    "Emergency Medicine": AlertTriangle,
    "Internal Medicine": Stethoscope,
    Neurology: Brain,
    Orthopedics: Activity,
    Psychiatry: Brain,
    Pulmonology: Activity,
    Gastroenterology: Pill,
    default: Stethoscope,
  };

  return (
    <div className="space-y-3">
      {sorted.slice(0, 6).map(([dept, count]) => {
        const Icon = deptIcons[dept] || deptIcons.default;
        const pct = (count / max) * 100;
        return (
          <div key={dept} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-slate-400" />
                <span className="text-slate-700 dark:text-slate-300">{dept}</span>
              </div>
              <span className="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
                {count}
              </span>
            </div>
            <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-teal-500 rounded-full transition-all duration-500"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Recent triage activity
function RecentTriageTable({ patients }: { patients: Patient[] }) {
  const recent = patients.slice(0, 8);

  const esiColors = {
    1: "bg-red-500",
    2: "bg-orange-500",
    3: "bg-amber-500",
    4: "bg-lime-500",
    5: "bg-green-500",
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 dark:border-slate-700">
            <th className="text-left py-3 px-2 font-medium text-slate-500">Patient</th>
            <th className="text-left py-3 px-2 font-medium text-slate-500">Chief Complaint</th>
            <th className="text-center py-3 px-2 font-medium text-slate-500">ESI</th>
            <th className="text-center py-3 px-2 font-medium text-slate-500">Confidence</th>
            <th className="text-left py-3 px-2 font-medium text-slate-500">Department</th>
            <th className="text-right py-3 px-2 font-medium text-slate-500">Arrived</th>
          </tr>
        </thead>
        <tbody>
          {recent.map((patient) => (
            <tr
              key={patient.id}
              className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
            >
              <td className="py-3 px-2">
                <div>
                  <p className="font-medium text-slate-900 dark:text-slate-100">{patient.name}</p>
                  <p className="text-xs text-slate-400">
                    {patient.age}{patient.gender} • {patient.abha.slice(0, 8)}...
                  </p>
                </div>
              </td>
              <td className="py-3 px-2 text-slate-600 dark:text-slate-400 max-w-48 truncate">
                {patient.chiefComplaint}
              </td>
              <td className="py-3 px-2 text-center">
                <span
                  className={cn(
                    "inline-flex h-7 w-7 items-center justify-center rounded-lg text-white font-bold text-xs",
                    esiColors[patient.aiDecision.esi as keyof typeof esiColors]
                  )}
                >
                  {patient.aiDecision.esi}
                </span>
              </td>
              <td className="py-3 px-2 text-center">
                <span
                  className={cn(
                    "font-semibold tabular-nums",
                    patient.aiDecision.confidence >= 85
                      ? "text-emerald-600"
                      : patient.aiDecision.confidence >= 70
                      ? "text-amber-600"
                      : "text-red-600"
                  )}
                >
                  {patient.aiDecision.confidence}%
                </span>
              </td>
              <td className="py-3 px-2 text-slate-600 dark:text-slate-400">
                {patient.aiDecision.specialists[0] || "—"}
              </td>
              <td className="py-3 px-2 text-right text-slate-400">
                {patient.arrivalTime}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Animated counter
function AnimatedCounter({ value }: { value: number }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 30;
    const increment = value / steps;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      setCurrent(Math.min(Math.round(increment * step), value));
      if (step >= steps) clearInterval(timer);
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  return <span className="tabular-nums">{current}</span>;
}

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const stats = computeStats(mockPatients);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-1.5 -ml-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </Link>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-teal-600" />
              <span className="font-semibold text-slate-900 dark:text-slate-100">
                Dashboard
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live</span>
            </div>
            <Link
              href="/queue"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 transition-colors"
            >
              Open Queue
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <SummaryCard
            title="Total Patients"
            value={mounted ? <AnimatedCounter value={stats.total} /> : 0}
            subtitle="In system today"
            icon={Users}
            trend="up"
            trendValue="+12%"
            color="teal"
          />
          <SummaryCard
            title="High Risk (ESI 1-2)"
            value={mounted ? <AnimatedCounter value={stats.highRisk} /> : 0}
            subtitle="Requires immediate attention"
            icon={AlertTriangle}
            trend="down"
            trendValue="-3%"
            color="red"
          />
          <SummaryCard
            title="Avg. Confidence"
            value={`${stats.avgConfidence}%`}
            subtitle="AI prediction accuracy"
            icon={Brain}
            trend="up"
            trendValue="+2.1%"
            color="violet"
          />
          <SummaryCard
            title="Avg. Triage Time"
            value="47s"
            subtitle="From arrival to decision"
            icon={Timer}
            trend="down"
            trendValue="-12s"
            color="emerald"
          />
        </div>

        {/* Risk Distribution */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-slate-400" />
            <h2 className="font-semibold text-slate-900 dark:text-slate-100">
              Risk Level Distribution
            </h2>
          </div>
          <RiskDistributionBar
            high={stats.highRisk}
            medium={stats.mediumRisk}
            low={stats.lowRisk}
            total={stats.total}
          />
        </div>

        {/* Charts Row */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* ESI Distribution */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <PieChart className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                ESI Level Breakdown
              </h2>
            </div>
            <ESIDonutChart byESI={stats.byESI} total={stats.total} />
          </div>

          {/* Department Distribution */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <Stethoscope className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                Department Insights
              </h2>
            </div>
            <DepartmentBarChart data={stats.byDepartment} />
          </div>
        </div>

        {/* Acuity Cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-xl border-2 border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-900/20 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-red-800 dark:text-red-300">Critical</span>
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <p className="text-4xl font-bold text-red-700 dark:text-red-400">
              {stats.byAcuity.critical}
            </p>
            <p className="text-xs text-red-600/70 dark:text-red-400/70 mt-1">
              ESI-1: Life-threatening
            </p>
          </div>
          <div className="rounded-xl border-2 border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-900/20 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-amber-800 dark:text-amber-300">Urgent</span>
              <Clock className="h-5 w-5 text-amber-600" />
            </div>
            <p className="text-4xl font-bold text-amber-700 dark:text-amber-400">
              {stats.byAcuity.urgent}
            </p>
            <p className="text-xs text-amber-600/70 dark:text-amber-400/70 mt-1">
              ESI-2/3: Time-sensitive
            </p>
          </div>
          <div className="rounded-xl border-2 border-emerald-200 dark:border-emerald-900/50 bg-emerald-50 dark:bg-emerald-900/20 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-emerald-800 dark:text-emerald-300">Minor</span>
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            </div>
            <p className="text-4xl font-bold text-emerald-700 dark:text-emerald-400">
              {stats.byAcuity.minor}
            </p>
            <p className="text-xs text-emerald-600/70 dark:text-emerald-400/70 mt-1">
              ESI-4/5: Non-urgent
            </p>
          </div>
        </div>

        {/* Recent Triage Activity */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                Recent Triage Activity
              </h2>
            </div>
            <Link
              href="/queue"
              className="text-sm text-teal-600 hover:text-teal-700 font-medium flex items-center gap-1"
            >
              View all
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
          <RecentTriageTable patients={mockPatients} />
        </div>
      </main>
    </div>
  );
}
