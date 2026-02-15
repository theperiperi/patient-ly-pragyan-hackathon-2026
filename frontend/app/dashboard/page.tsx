"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { mockPatients } from "@/lib/mock-data";
import { Patient } from "@/lib/types";
import {
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  ChevronRight,
  Clock,
  AlertTriangle,
  Activity,
  Users,
  Zap,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ============================================
// DATA PROCESSING
// ============================================

interface DepartmentStats {
  name: string;
  total: number;
  critical: number;
  urgent: number;
  pending: number;
  avgWait: number;
  avgConfidence: number;
  trend: "up" | "down" | "stable";
}

interface HourlyDataPoint {
  hour: string;
  arrivals: number;
  discharged: number;
  critical: number;
}

function computeDashboardData(patients: Patient[]) {
  // Overall stats
  const stats = {
    total: patients.length,
    critical: 0,
    urgent: 0,
    minor: 0,
    pendingReview: Math.floor(patients.length * 0.15),
    avgWaitTime: 0,
    avgConfidence: 0,
    byESI: [0, 0, 0, 0, 0, 0] as number[],
    departments: {} as Record<string, DepartmentStats>,
  };

  let totalConfidence = 0;
  let totalWait = 0;

  patients.forEach((p, idx) => {
    // Acuity counts
    if (p.aiDecision.acuityColor === "critical") stats.critical++;
    else if (p.aiDecision.acuityColor === "urgent") stats.urgent++;
    else stats.minor++;

    // ESI breakdown
    stats.byESI[p.aiDecision.esi]++;

    // Confidence
    totalConfidence += p.aiDecision.confidence;

    // Simulated wait time (minutes)
    const waitTime = 5 + Math.floor(Math.random() * 45);
    totalWait += waitTime;

    // Department aggregation
    const dept = p.aiDecision.specialists[0] || "General";
    if (!stats.departments[dept]) {
      stats.departments[dept] = {
        name: dept,
        total: 0,
        critical: 0,
        urgent: 0,
        pending: 0,
        avgWait: 0,
        avgConfidence: 0,
        trend: ["up", "down", "stable"][Math.floor(Math.random() * 3)] as "up" | "down" | "stable",
      };
    }
    stats.departments[dept].total++;
    if (p.aiDecision.esi <= 2) stats.departments[dept].critical++;
    if (p.aiDecision.acuityColor === "urgent") stats.departments[dept].urgent++;
    stats.departments[dept].avgConfidence += p.aiDecision.confidence;
    stats.departments[dept].avgWait += waitTime;
    if (idx % 7 === 0) stats.departments[dept].pending++;
  });

  // Finalize department averages
  Object.values(stats.departments).forEach(dept => {
    dept.avgConfidence = Math.round(dept.avgConfidence / dept.total);
    dept.avgWait = Math.round(dept.avgWait / dept.total);
  });

  stats.avgConfidence = Math.round(totalConfidence / patients.length);
  stats.avgWaitTime = Math.round(totalWait / patients.length);

  return stats;
}

function generateHourlyData(): HourlyDataPoint[] {
  const data: HourlyDataPoint[] = [];
  const now = new Date();
  for (let i = 11; i >= 0; i--) {
    const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
    data.push({
      hour: hour.getHours().toString().padStart(2, "0") + ":00",
      arrivals: Math.floor(4 + Math.random() * 8),
      discharged: Math.floor(3 + Math.random() * 6),
      critical: Math.floor(Math.random() * 3),
    });
  }
  return data;
}

// ============================================
// MINI COMPONENTS
// ============================================

function MiniSparkline({ data, color = "#10b981", height = 24 }: { data: number[]; color?: string; height?: number }) {
  const max = Math.max(...data, 1);
  const width = 64;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * width},${height - (v / max) * height}`).join(" ");

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        points={points}
      />
    </svg>
  );
}

function StatusDot({ status }: { status: "critical" | "urgent" | "normal" | "pending" }) {
  const colors = {
    critical: "bg-red-500",
    urgent: "bg-amber-500",
    normal: "bg-emerald-500",
    pending: "bg-slate-400",
  };
  return <span className={cn("inline-block w-1.5 h-1.5 rounded-full", colors[status])} />;
}

function TrendIndicator({ trend, value }: { trend: "up" | "down" | "stable"; value?: string }) {
  if (trend === "up") return <span className="text-emerald-600 text-[10px] flex items-center gap-0.5"><ArrowUpRight className="w-3 h-3" />{value}</span>;
  if (trend === "down") return <span className="text-red-500 text-[10px] flex items-center gap-0.5"><ArrowDownRight className="w-3 h-3" />{value}</span>;
  return <span className="text-slate-400 text-[10px] flex items-center gap-0.5"><Minus className="w-3 h-3" />{value}</span>;
}

function ProgressBar({ value, max, color = "bg-teal-600" }: { value: number; max: number; color?: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="h-1 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden w-full">
      <div className={cn("h-full rounded-full", color)} style={{ width: `${pct}%` }} />
    </div>
  );
}

// ============================================
// MAIN DASHBOARD
// ============================================

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  const stats = useMemo(() => computeDashboardData(mockPatients), []);
  const hourlyData = useMemo(() => generateHourlyData(), []);
  const departmentList = useMemo(() =>
    Object.values(stats.departments).sort((a, b) => b.total - a.total),
    [stats.departments]
  );

  useEffect(() => {
    setMounted(true);
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  if (!mounted) {
    return <div className="min-h-screen bg-slate-100 dark:bg-slate-950" />;
  }

  const timeStr = currentTime.toLocaleTimeString("en-US", { hour12: false });
  const dateStr = currentTime.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-[#0a0f1a] text-slate-900 dark:text-slate-100">
      {/* ============================================ */}
      {/* TOP BAR - Compact header                    */}
      {/* ============================================ */}
      <header className="h-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-3 text-xs">
        <div className="flex items-center gap-4">
          <Link href="/" className="font-semibold text-slate-700 dark:text-slate-200 hover:text-teal-600 transition-colors">
            Patient.ly
          </Link>
          <span className="text-slate-400 dark:text-slate-600">|</span>
          <span className="text-slate-500 dark:text-slate-400">Operations Dashboard</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-slate-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] uppercase tracking-wider">Live</span>
          </div>
          <span className="text-slate-400 dark:text-slate-500 font-mono">{dateStr}</span>
          <span className="text-slate-700 dark:text-slate-300 font-mono font-medium">{timeStr}</span>
          <Link
            href="/queue"
            className="ml-2 px-2.5 py-1 bg-slate-800 dark:bg-slate-700 text-white text-[10px] uppercase tracking-wide rounded hover:bg-slate-700 dark:hover:bg-slate-600 transition-colors flex items-center gap-1"
          >
            Queue <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
      </header>

      {/* ============================================ */}
      {/* KPI STRIP - Key metrics in single row       */}
      {/* ============================================ */}
      <div className="h-14 bg-white dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 flex items-center px-3 gap-6">
        {/* Total Patients */}
        <div className="flex items-center gap-3 pr-6 border-r border-slate-200 dark:border-slate-700">
          <div className="w-8 h-8 rounded bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
            <Users className="w-4 h-4 text-slate-500" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Census</div>
            <div className="text-lg font-semibold font-mono tabular-nums">{stats.total}</div>
          </div>
          <TrendIndicator trend="up" value="+8%" />
        </div>

        {/* Critical */}
        <div className="flex items-center gap-3 pr-6 border-r border-slate-200 dark:border-slate-700">
          <div className="w-8 h-8 rounded bg-red-50 dark:bg-red-950/50 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-red-600" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Critical</div>
            <div className="text-lg font-semibold font-mono tabular-nums text-red-600">{stats.critical}</div>
          </div>
          <MiniSparkline data={hourlyData.map(h => h.critical)} color="#ef4444" />
        </div>

        {/* Pending Review */}
        <div className="flex items-center gap-3 pr-6 border-r border-slate-200 dark:border-slate-700">
          <div className="w-8 h-8 rounded bg-amber-50 dark:bg-amber-950/50 flex items-center justify-center">
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Pending</div>
            <div className="text-lg font-semibold font-mono tabular-nums text-amber-600">{stats.pendingReview}</div>
          </div>
        </div>

        {/* Avg Wait */}
        <div className="flex items-center gap-3 pr-6 border-r border-slate-200 dark:border-slate-700">
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Avg Wait</div>
            <div className="text-lg font-semibold font-mono tabular-nums">{stats.avgWaitTime}<span className="text-xs text-slate-400 ml-0.5">min</span></div>
          </div>
          <TrendIndicator trend="down" value="-12%" />
        </div>

        {/* AI Confidence */}
        <div className="flex items-center gap-3 pr-6 border-r border-slate-200 dark:border-slate-700">
          <div className="w-8 h-8 rounded bg-teal-50 dark:bg-teal-950/50 flex items-center justify-center">
            <Zap className="w-4 h-4 text-teal-600" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wide">AI Conf.</div>
            <div className="text-lg font-semibold font-mono tabular-nums text-teal-600">{stats.avgConfidence}%</div>
          </div>
        </div>

        {/* Throughput */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-emerald-50 dark:bg-emerald-950/50 flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Throughput</div>
            <div className="text-lg font-semibold font-mono tabular-nums text-emerald-600">{hourlyData.reduce((s, h) => s + h.discharged, 0)}<span className="text-xs text-slate-400 ml-0.5">/12h</span></div>
          </div>
          <MiniSparkline data={hourlyData.map(h => h.discharged)} color="#10b981" />
        </div>
      </div>

      {/* ============================================ */}
      {/* MAIN CONTENT GRID                           */}
      {/* ============================================ */}
      <div className="p-2 grid grid-cols-12 gap-2 h-[calc(100vh-96px)]">

        {/* LEFT COLUMN - Department Overview */}
        <div className="col-span-4 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden">
          <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Department Overview</span>
            <span className="text-[10px] text-slate-400">{departmentList.length} active</span>
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-[11px]">
              <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/80 z-10">
                <tr className="text-slate-500 dark:text-slate-400">
                  <th className="text-left py-1.5 px-2 font-medium">Dept</th>
                  <th className="text-center py-1.5 px-1 font-medium w-10">Tot</th>
                  <th className="text-center py-1.5 px-1 font-medium w-10">Crit</th>
                  <th className="text-center py-1.5 px-1 font-medium w-10">Pnd</th>
                  <th className="text-center py-1.5 px-1 font-medium w-12">Wait</th>
                  <th className="text-center py-1.5 px-1 font-medium w-12">Conf</th>
                  <th className="text-left py-1.5 px-2 font-medium w-20">Load</th>
                </tr>
              </thead>
              <tbody>
                {departmentList.map((dept, idx) => (
                  <tr
                    key={dept.name}
                    className={cn(
                      "border-t border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/30 cursor-pointer transition-colors",
                      idx % 2 === 0 ? "" : "bg-slate-50/50 dark:bg-slate-800/20"
                    )}
                  >
                    <td className="py-1.5 px-2">
                      <div className="flex items-center gap-1.5">
                        <TrendIndicator trend={dept.trend} />
                        <span className="font-medium text-slate-700 dark:text-slate-200 truncate max-w-[100px]">{dept.name}</span>
                      </div>
                    </td>
                    <td className="text-center py-1.5 px-1 font-mono tabular-nums">{dept.total}</td>
                    <td className="text-center py-1.5 px-1">
                      {dept.critical > 0 ? (
                        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] rounded text-[10px] font-semibold bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-400">
                          {dept.critical}
                        </span>
                      ) : (
                        <span className="text-slate-300 dark:text-slate-600">—</span>
                      )}
                    </td>
                    <td className="text-center py-1.5 px-1 text-amber-600 font-mono tabular-nums">{dept.pending || "—"}</td>
                    <td className="text-center py-1.5 px-1 font-mono tabular-nums text-slate-600 dark:text-slate-400">{dept.avgWait}m</td>
                    <td className="text-center py-1.5 px-1">
                      <span className={cn(
                        "font-mono tabular-nums font-medium",
                        dept.avgConfidence >= 85 ? "text-emerald-600" : dept.avgConfidence >= 75 ? "text-amber-600" : "text-red-500"
                      )}>
                        {dept.avgConfidence}%
                      </span>
                    </td>
                    <td className="py-1.5 px-2">
                      <ProgressBar
                        value={dept.total}
                        max={Math.max(...departmentList.map(d => d.total))}
                        color={dept.critical > 2 ? "bg-red-500" : dept.critical > 0 ? "bg-amber-500" : "bg-teal-500"}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* CENTER COLUMN - ESI + Activity */}
        <div className="col-span-5 flex flex-col gap-2">

          {/* ESI Distribution */}
          <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 flex-shrink-0">
            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">ESI Distribution</span>
              <div className="flex items-center gap-3 text-[10px] text-slate-400">
                <span>1-Resus</span>
                <span>2-Emerg</span>
                <span>3-Urgent</span>
                <span>4-Less</span>
                <span>5-Non</span>
              </div>
            </div>
            <div className="p-3">
              <div className="flex items-end gap-1 h-20">
                {[1, 2, 3, 4, 5].map(esi => {
                  const count = stats.byESI[esi];
                  const maxCount = Math.max(...stats.byESI.slice(1));
                  const height = maxCount > 0 ? (count / maxCount) * 100 : 0;
                  const colors = ["", "bg-red-600", "bg-orange-500", "bg-amber-500", "bg-lime-500", "bg-emerald-500"];
                  return (
                    <div key={esi} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        className={cn("w-full rounded-t transition-all", colors[esi])}
                        style={{ height: `${Math.max(height, 4)}%` }}
                      />
                      <div className="text-[10px] font-mono tabular-nums text-slate-600 dark:text-slate-400">{count}</div>
                      <div className={cn(
                        "text-[9px] font-bold text-white w-4 h-4 rounded flex items-center justify-center",
                        colors[esi]
                      )}>
                        {esi}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Hourly Flow Chart */}
          <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Patient Flow (12h)</span>
              <div className="flex items-center gap-3 text-[10px]">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-teal-500" />Arrivals</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-slate-400" />Discharged</span>
              </div>
            </div>
            <div className="p-3 h-28">
              <div className="flex items-end gap-0.5 h-full">
                {hourlyData.map((d, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                    <div className="w-full flex flex-col gap-0.5 flex-1 justify-end">
                      <div
                        className="w-full bg-teal-500 rounded-t"
                        style={{ height: `${(d.arrivals / 12) * 100}%` }}
                      />
                    </div>
                    <div className="text-[8px] text-slate-400 font-mono">{d.hour.slice(0, 2)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Activity Table */}
          <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 flex-1 flex flex-col overflow-hidden">
            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Recent Triage Activity</span>
              <Link href="/queue" className="text-[10px] text-teal-600 hover:text-teal-700 flex items-center gap-0.5">
                View All <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="flex-1 overflow-auto">
              <table className="w-full text-[11px]">
                <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/80 z-10">
                  <tr className="text-slate-500 dark:text-slate-400">
                    <th className="text-left py-1.5 px-2 font-medium">Patient</th>
                    <th className="text-left py-1.5 px-2 font-medium">Complaint</th>
                    <th className="text-center py-1.5 px-1 font-medium w-8">ESI</th>
                    <th className="text-center py-1.5 px-1 font-medium w-12">Conf</th>
                    <th className="text-left py-1.5 px-2 font-medium">Dept</th>
                    <th className="text-right py-1.5 px-2 font-medium w-16">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {mockPatients.slice(0, 15).map((patient, idx) => (
                    <tr
                      key={patient.id}
                      className={cn(
                        "border-t border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/30 cursor-pointer transition-colors",
                        idx % 2 === 0 ? "" : "bg-slate-50/50 dark:bg-slate-800/20"
                      )}
                    >
                      <td className="py-1.5 px-2">
                        <div className="flex items-center gap-1.5">
                          <StatusDot status={patient.aiDecision.acuityColor === "critical" ? "critical" : patient.aiDecision.acuityColor === "urgent" ? "urgent" : "normal"} />
                          <span className="font-medium text-slate-700 dark:text-slate-200">{patient.name}</span>
                          <span className="text-slate-400 text-[10px]">{patient.age}{patient.gender}</span>
                        </div>
                      </td>
                      <td className="py-1.5 px-2 text-slate-500 dark:text-slate-400 truncate max-w-[140px]">{patient.chiefComplaint}</td>
                      <td className="py-1.5 px-1 text-center">
                        <span className={cn(
                          "inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-bold text-white",
                          patient.aiDecision.esi === 1 ? "bg-red-600" :
                          patient.aiDecision.esi === 2 ? "bg-orange-500" :
                          patient.aiDecision.esi === 3 ? "bg-amber-500" :
                          patient.aiDecision.esi === 4 ? "bg-lime-500" : "bg-emerald-500"
                        )}>
                          {patient.aiDecision.esi}
                        </span>
                      </td>
                      <td className="py-1.5 px-1 text-center">
                        <span className={cn(
                          "font-mono tabular-nums font-medium text-[10px]",
                          patient.aiDecision.confidence >= 85 ? "text-emerald-600" :
                          patient.aiDecision.confidence >= 75 ? "text-amber-600" : "text-red-500"
                        )}>
                          {patient.aiDecision.confidence}%
                        </span>
                      </td>
                      <td className="py-1.5 px-2 text-slate-500 dark:text-slate-400 truncate max-w-[80px]">{patient.aiDecision.specialists[0] || "—"}</td>
                      <td className="py-1.5 px-2 text-right text-slate-400 text-[10px] font-mono">{patient.arrivalTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN - Alerts & Stats */}
        <div className="col-span-3 flex flex-col gap-2">

          {/* Risk Summary Cards */}
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-red-50 dark:bg-red-950/30 rounded border border-red-100 dark:border-red-900/50 p-2">
              <div className="text-[10px] text-red-600 dark:text-red-400 uppercase tracking-wide">Critical</div>
              <div className="text-xl font-bold font-mono tabular-nums text-red-700 dark:text-red-400">{stats.critical}</div>
              <div className="text-[10px] text-red-500">{Math.round(stats.critical / stats.total * 100)}%</div>
            </div>
            <div className="bg-amber-50 dark:bg-amber-950/30 rounded border border-amber-100 dark:border-amber-900/50 p-2">
              <div className="text-[10px] text-amber-600 dark:text-amber-400 uppercase tracking-wide">Urgent</div>
              <div className="text-xl font-bold font-mono tabular-nums text-amber-700 dark:text-amber-400">{stats.urgent}</div>
              <div className="text-[10px] text-amber-500">{Math.round(stats.urgent / stats.total * 100)}%</div>
            </div>
            <div className="bg-emerald-50 dark:bg-emerald-950/30 rounded border border-emerald-100 dark:border-emerald-900/50 p-2">
              <div className="text-[10px] text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">Minor</div>
              <div className="text-xl font-bold font-mono tabular-nums text-emerald-700 dark:text-emerald-400">{stats.minor}</div>
              <div className="text-[10px] text-emerald-500">{Math.round(stats.minor / stats.total * 100)}%</div>
            </div>
          </div>

          {/* Active Alerts */}
          <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 flex-1 flex flex-col overflow-hidden">
            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Active Alerts</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-400 font-medium">{stats.critical + Math.floor(stats.urgent / 2)}</span>
            </div>
            <div className="flex-1 overflow-auto p-2 space-y-1.5">
              {mockPatients.filter(p => p.aiDecision.esi <= 2).slice(0, 8).map(patient => (
                <div
                  key={patient.id}
                  className={cn(
                    "p-2 rounded border text-[11px] cursor-pointer hover:shadow-sm transition-shadow",
                    patient.aiDecision.esi === 1
                      ? "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900/50"
                      : "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/50"
                  )}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-700 dark:text-slate-200">{patient.name}</span>
                    <span className={cn(
                      "text-[9px] font-bold px-1 py-0.5 rounded text-white",
                      patient.aiDecision.esi === 1 ? "bg-red-600" : "bg-orange-500"
                    )}>
                      ESI-{patient.aiDecision.esi}
                    </span>
                  </div>
                  <div className="text-slate-500 dark:text-slate-400 truncate">{patient.chiefComplaint}</div>
                  <div className="flex items-center justify-between mt-1 text-[10px] text-slate-400">
                    <span>{patient.aiDecision.bay}</span>
                    <span>{patient.arrivalTime}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Arrival Mode */}
          <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 p-3">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400 mb-2">Arrival Mode</div>
            <div className="space-y-2">
              {[
                { label: "Ambulance", count: mockPatients.filter(p => p.arrivalMode === "Ambulance").length, color: "bg-red-500" },
                { label: "Walk-in", count: mockPatients.filter(p => p.arrivalMode === "Walk-in").length, color: "bg-slate-500" },
                { label: "Referral", count: mockPatients.filter(p => p.arrivalMode === "Referral").length, color: "bg-teal-500" },
              ].map(mode => (
                <div key={mode.label} className="flex items-center gap-2">
                  <span className="text-[10px] text-slate-500 w-16">{mode.label}</span>
                  <div className="flex-1">
                    <ProgressBar value={mode.count} max={stats.total} color={mode.color} />
                  </div>
                  <span className="text-[10px] font-mono tabular-nums text-slate-600 dark:text-slate-400 w-6 text-right">{mode.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Performance */}
          <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 p-3">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400 mb-2">AI Performance</div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-[10px] text-slate-400">Avg Confidence</div>
                <div className="text-lg font-bold font-mono tabular-nums text-teal-600">{stats.avgConfidence}%</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400">High Conf (&gt;85%)</div>
                <div className="text-lg font-bold font-mono tabular-nums text-emerald-600">
                  {mockPatients.filter(p => p.aiDecision.confidence >= 85).length}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400">Low Conf (&lt;75%)</div>
                <div className="text-lg font-bold font-mono tabular-nums text-red-500">
                  {mockPatients.filter(p => p.aiDecision.confidence < 75).length}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400">Override Rate</div>
                <div className="text-lg font-bold font-mono tabular-nums text-slate-600">4.2%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
