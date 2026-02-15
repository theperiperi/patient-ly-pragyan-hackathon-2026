"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { mockPatients } from "@/lib/mock-data";
import { Patient } from "@/lib/types";
import {
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  Clock,
  AlertTriangle,
  Users,
  Zap,
  TrendingUp,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  Line,
  ComposedChart,
} from "recharts";

// ============================================
// DATA PROCESSING
// ============================================

function generateHourlyFlow() {
  const data = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hourLabel = hour.getHours().toString().padStart(2, "0") + ":00";
    const timeOfDay = hour.getHours();
    const baseFactor = timeOfDay >= 8 && timeOfDay <= 20 ? 1.5 : 0.7;
    const arrivals = Math.floor((4 + Math.random() * 6) * baseFactor);
    const discharged = Math.floor((3 + Math.random() * 5) * baseFactor);
    const critical = Math.floor(Math.random() * 3 * baseFactor);
    data.push({ hour: hourLabel, arrivals, discharged, critical });
  }
  return data;
}

function computeStats(patients: Patient[]) {
  const stats = {
    total: patients.length,
    critical: 0,
    urgent: 0,
    minor: 0,
    pendingReview: Math.floor(patients.length * 0.15),
    avgWaitTime: Math.floor(15 + Math.random() * 10),
    avgConfidence: 0,
    byESI: [
      { esi: "ESI-1", count: 0, label: "Resuscitation", color: "#dc2626" },
      { esi: "ESI-2", count: 0, label: "Emergent", color: "#ea580c" },
      { esi: "ESI-3", count: 0, label: "Urgent", color: "#d97706" },
      { esi: "ESI-4", count: 0, label: "Less Urgent", color: "#84cc16" },
      { esi: "ESI-5", count: 0, label: "Non-Urgent", color: "#22c55e" },
    ],
    byDepartment: {} as Record<string, { total: number; critical: number; avgConf: number }>,
  };

  let totalConf = 0;

  patients.forEach(p => {
    if (p.aiDecision.acuityColor === "critical") stats.critical++;
    else if (p.aiDecision.acuityColor === "urgent") stats.urgent++;
    else stats.minor++;

    const esiIdx = p.aiDecision.esi - 1;
    if (esiIdx >= 0 && esiIdx < 5) stats.byESI[esiIdx].count++;

    totalConf += p.aiDecision.confidence;

    const dept = p.aiDecision.specialists[0] || "General";
    if (!stats.byDepartment[dept]) {
      stats.byDepartment[dept] = { total: 0, critical: 0, avgConf: 0 };
    }
    stats.byDepartment[dept].total++;
    if (p.aiDecision.esi <= 2) stats.byDepartment[dept].critical++;
    stats.byDepartment[dept].avgConf += p.aiDecision.confidence;
  });

  Object.values(stats.byDepartment).forEach(d => {
    d.avgConf = Math.round(d.avgConf / d.total);
  });
  stats.avgConfidence = Math.round(totalConf / patients.length);

  return stats;
}

// ============================================
// MAIN DASHBOARD
// ============================================

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  const stats = useMemo(() => computeStats(mockPatients), []);
  const hourlyFlow = useMemo(() => generateHourlyFlow(), []);

  const departmentList = useMemo(() =>
    Object.entries(stats.byDepartment)
      .map(([name, data]) => ({ name, ...data }))
      .sort((a, b) => b.total - a.total),
    [stats.byDepartment]
  );

  useEffect(() => {
    setMounted(true);
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  if (!mounted) {
    return <div className="min-h-screen bg-slate-50 dark:bg-slate-950" />;
  }

  const timeStr = currentTime.toLocaleTimeString("en-US", { hour12: false });
  const dateStr = currentTime.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* HEADER */}
      <header className="h-12 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <Link href="/" className="font-semibold text-slate-800 dark:text-slate-200 hover:text-teal-600 transition-colors">
            Patient.ly
          </Link>
          <span className="text-slate-300 dark:text-slate-700">|</span>
          <span className="text-sm text-slate-600 dark:text-slate-400">Operations Dashboard</span>
        </div>
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Live</span>
          </div>
          <span className="text-sm text-slate-500 font-mono">{dateStr} {timeStr}</span>
          <Link href="/queue" className="px-3 py-1.5 bg-slate-800 dark:bg-slate-700 text-white text-xs font-medium rounded hover:bg-slate-700 dark:hover:bg-slate-600 transition-colors flex items-center gap-1">
            Open Queue <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      <main className="p-4 space-y-4 max-w-[1600px] mx-auto">

        {/* ROW 1: KPI Cards */}
        <div className="grid grid-cols-6 gap-4">
          <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                <Users className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </div>
              <div>
                <div className="text-xs text-slate-500 uppercase tracking-wide">Census</div>
                <div className="text-2xl font-bold font-mono">{stats.total}</div>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-1 text-xs text-emerald-600">
              <ArrowUpRight className="w-3.5 h-3.5" />
              <span>+8% vs last hour</span>
            </div>
          </div>

          <div className="bg-red-50 dark:bg-red-950/30 rounded-lg border border-red-200 dark:border-red-900/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-100 dark:bg-red-900/50 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <div className="text-xs text-red-600 dark:text-red-400 uppercase tracking-wide">Critical</div>
                <div className="text-2xl font-bold font-mono text-red-700 dark:text-red-400">{stats.critical}</div>
              </div>
            </div>
            <div className="mt-2 text-xs text-red-600/70">{Math.round(stats.critical / stats.total * 100)}% of total</div>
          </div>

          <div className="bg-amber-50 dark:bg-amber-950/30 rounded-lg border border-amber-200 dark:border-amber-900/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/50 flex items-center justify-center">
                <Clock className="w-5 h-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <div className="text-xs text-amber-600 dark:text-amber-400 uppercase tracking-wide">Pending</div>
                <div className="text-2xl font-bold font-mono text-amber-700 dark:text-amber-400">{stats.pendingReview}</div>
              </div>
            </div>
            <div className="mt-2 text-xs text-amber-600/70">Awaiting review</div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                <Activity className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </div>
              <div>
                <div className="text-xs text-slate-500 uppercase tracking-wide">Avg Wait</div>
                <div className="text-2xl font-bold font-mono">{stats.avgWaitTime}<span className="text-sm text-slate-400 ml-1">min</span></div>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-1 text-xs text-emerald-600">
              <ArrowDownRight className="w-3.5 h-3.5" />
              <span>-12% improvement</span>
            </div>
          </div>

          <div className="bg-teal-50 dark:bg-teal-950/30 rounded-lg border border-teal-200 dark:border-teal-900/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-teal-100 dark:bg-teal-900/50 flex items-center justify-center">
                <Zap className="w-5 h-5 text-teal-600 dark:text-teal-400" />
              </div>
              <div>
                <div className="text-xs text-teal-600 dark:text-teal-400 uppercase tracking-wide">AI Confidence</div>
                <div className="text-2xl font-bold font-mono text-teal-700 dark:text-teal-400">{stats.avgConfidence}%</div>
              </div>
            </div>
            <div className="mt-2 text-xs text-teal-600/70">Average score</div>
          </div>

          <div className="bg-emerald-50 dark:bg-emerald-950/30 rounded-lg border border-emerald-200 dark:border-emerald-900/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <div className="text-xs text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">Throughput</div>
                <div className="text-2xl font-bold font-mono text-emerald-700 dark:text-emerald-400">{hourlyFlow.slice(-12).reduce((s, h) => s + h.discharged, 0)}</div>
              </div>
            </div>
            <div className="mt-2 text-xs text-emerald-600/70">Discharged (12h)</div>
          </div>
        </div>

        {/* ROW 2: Charts */}
        <div className="grid grid-cols-12 gap-4">
          {/* Patient Flow Chart */}
          <div className="col-span-8 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800">
            <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Patient Flow (24h)</h3>
              <div className="flex items-center gap-4 text-xs">
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-teal-500" />Arrivals</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500" />Discharged</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-0.5 bg-red-500" />Critical</span>
              </div>
            </div>
            <div className="p-4 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={hourlyFlow}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="hour" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={2} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }} />
                  <Area type="monotone" dataKey="arrivals" fill="#0d9488" fillOpacity={0.2} stroke="#0d9488" strokeWidth={2} name="Arrivals" />
                  <Area type="monotone" dataKey="discharged" fill="#3b82f6" fillOpacity={0.15} stroke="#3b82f6" strokeWidth={2} name="Discharged" />
                  <Line type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2} dot={false} name="Critical" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* ESI Distribution */}
          <div className="col-span-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800">
            <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">ESI Distribution</h3>
            </div>
            <div className="p-4 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.byESI} layout="vertical" barSize={20}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={true} vertical={false} />
                  <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis type="category" dataKey="esi" tick={{ fontSize: 11, fill: '#64748b' }} width={50} />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} name="Patients">
                    {stats.byESI.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ROW 3: Tables */}
        <div className="grid grid-cols-12 gap-4">
          {/* Department Table */}
          <div className="col-span-5 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800">
            <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Department Overview</h3>
              <span className="text-xs text-slate-400">{departmentList.length} departments</span>
            </div>
            <div className="overflow-auto max-h-64">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/80">
                  <tr className="text-xs text-slate-500">
                    <th className="text-left py-2.5 px-4 font-medium">Department</th>
                    <th className="text-center py-2.5 px-3 font-medium">Patients</th>
                    <th className="text-center py-2.5 px-3 font-medium">Critical</th>
                    <th className="text-center py-2.5 px-3 font-medium">AI Conf</th>
                    <th className="text-left py-2.5 px-3 font-medium">Load</th>
                  </tr>
                </thead>
                <tbody>
                  {departmentList.map((dept, idx) => (
                    <tr key={dept.name} className={cn("border-t border-slate-100 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/30", idx % 2 === 1 && "bg-slate-50/50 dark:bg-slate-800/20")}>
                      <td className="py-2.5 px-4 font-medium text-slate-700 dark:text-slate-200">{dept.name}</td>
                      <td className="py-2.5 px-3 text-center font-mono">{dept.total}</td>
                      <td className="py-2.5 px-3 text-center">
                        {dept.critical > 0 ? (
                          <span className="inline-flex items-center justify-center min-w-[22px] h-[22px] rounded text-xs font-semibold bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-400">{dept.critical}</span>
                        ) : <span className="text-slate-300 dark:text-slate-600">—</span>}
                      </td>
                      <td className="py-2.5 px-3 text-center">
                        <span className={cn("font-mono font-medium", dept.avgConf >= 85 ? "text-emerald-600" : dept.avgConf >= 75 ? "text-amber-600" : "text-red-500")}>
                          {dept.avgConf}%
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden w-20">
                          <div
                            className={cn("h-full rounded-full transition-all", dept.critical > 2 ? "bg-red-500" : dept.critical > 0 ? "bg-amber-500" : "bg-teal-500")}
                            style={{ width: `${(dept.total / Math.max(...departmentList.map(d => d.total))) * 100}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="col-span-7 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800">
            <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Recent Triage Activity</h3>
              <Link href="/queue" className="text-xs text-teal-600 hover:text-teal-700 flex items-center gap-1">
                View All <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <div className="overflow-auto max-h-64">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/80">
                  <tr className="text-xs text-slate-500">
                    <th className="text-left py-2.5 px-4 font-medium">Patient</th>
                    <th className="text-left py-2.5 px-3 font-medium">Complaint</th>
                    <th className="text-center py-2.5 px-2 font-medium">ESI</th>
                    <th className="text-center py-2.5 px-2 font-medium">Conf</th>
                    <th className="text-left py-2.5 px-3 font-medium">Dept</th>
                    <th className="text-right py-2.5 px-4 font-medium">Arrived</th>
                  </tr>
                </thead>
                <tbody>
                  {mockPatients.slice(0, 8).map((patient, idx) => (
                    <tr key={patient.id} className={cn("border-t border-slate-100 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/30 cursor-pointer", idx % 2 === 1 && "bg-slate-50/50 dark:bg-slate-800/20")}>
                      <td className="py-2.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className={cn("w-2 h-2 rounded-full flex-shrink-0", patient.aiDecision.acuityColor === "critical" ? "bg-red-500" : patient.aiDecision.acuityColor === "urgent" ? "bg-amber-500" : "bg-emerald-500")} />
                          <span className="font-medium text-slate-700 dark:text-slate-200">{patient.name}</span>
                          <span className="text-slate-400 text-xs">{patient.age}{patient.gender}</span>
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400 truncate max-w-[160px]">{patient.chiefComplaint}</td>
                      <td className="py-2.5 px-2 text-center">
                        <span className={cn(
                          "inline-flex items-center justify-center w-6 h-6 rounded text-xs font-bold text-white",
                          patient.aiDecision.esi === 1 ? "bg-red-600" : patient.aiDecision.esi === 2 ? "bg-orange-500" : patient.aiDecision.esi === 3 ? "bg-amber-500" : patient.aiDecision.esi === 4 ? "bg-lime-500" : "bg-emerald-500"
                        )}>
                          {patient.aiDecision.esi}
                        </span>
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <span className={cn("font-mono font-medium", patient.aiDecision.confidence >= 85 ? "text-emerald-600" : patient.aiDecision.confidence >= 75 ? "text-amber-600" : "text-red-500")}>
                          {patient.aiDecision.confidence}%
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400 truncate max-w-[90px]">{patient.aiDecision.specialists[0] || "—"}</td>
                      <td className="py-2.5 px-4 text-right text-slate-400 text-xs font-mono">{patient.arrivalTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* ROW 4: Risk Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950/40 dark:to-red-900/20 rounded-lg border border-red-200 dark:border-red-900/50 p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-red-700 dark:text-red-400">Critical Cases (ESI 1-2)</div>
                <div className="text-4xl font-bold text-red-800 dark:text-red-300 mt-1 font-mono">{stats.critical}</div>
                <div className="text-xs text-red-600/70 mt-2">Immediate attention required</div>
              </div>
              <div className="w-16 h-16 rounded-full bg-red-200/50 dark:bg-red-800/30 flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-950/40 dark:to-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-900/50 p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-amber-700 dark:text-amber-400">Urgent Cases (ESI 3)</div>
                <div className="text-4xl font-bold text-amber-800 dark:text-amber-300 mt-1 font-mono">{stats.urgent}</div>
                <div className="text-xs text-amber-600/70 mt-2">Priority monitoring needed</div>
              </div>
              <div className="w-16 h-16 rounded-full bg-amber-200/50 dark:bg-amber-800/30 flex items-center justify-center">
                <Clock className="w-8 h-8 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950/40 dark:to-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-900/50 p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-emerald-700 dark:text-emerald-400">Minor Cases (ESI 4-5)</div>
                <div className="text-4xl font-bold text-emerald-800 dark:text-emerald-300 mt-1 font-mono">{stats.minor}</div>
                <div className="text-xs text-emerald-600/70 mt-2">Standard queue processing</div>
              </div>
              <div className="w-16 h-16 rounded-full bg-emerald-200/50 dark:bg-emerald-800/30 flex items-center justify-center">
                <Activity className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
              </div>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
