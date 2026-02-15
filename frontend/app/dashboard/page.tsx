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
  LineChart,
  Line,
  PieChart,
  Pie,
  Legend,
  ComposedChart,
} from "recharts";

// ============================================
// DATA GENERATION
// ============================================

function generateHourlyFlow() {
  const data = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hourLabel = hour.getHours().toString().padStart(2, "0") + ":00";
    // Realistic ED pattern - busy during day, quieter at night
    const timeOfDay = hour.getHours();
    const baseFactor = timeOfDay >= 8 && timeOfDay <= 20 ? 1.5 : 0.7;
    const arrivals = Math.floor((4 + Math.random() * 6) * baseFactor);
    const discharged = Math.floor((3 + Math.random() * 5) * baseFactor);
    const critical = Math.floor(Math.random() * 3 * baseFactor);
    const pending = Math.max(0, Math.floor((arrivals - discharged) * 0.3 + Math.random() * 2));
    data.push({ hour: hourLabel, arrivals, discharged, critical, pending });
  }
  return data;
}

function generateDepartmentTimeSeries() {
  const departments = ["Cardiology", "Neurology", "Orthopedics", "Pulmonology", "General"];
  const data = [];
  for (let i = 11; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 60 * 60 * 1000);
    const entry: Record<string, number | string> = {
      hour: hour.getHours().toString().padStart(2, "0") + ":00",
    };
    departments.forEach(dept => {
      entry[dept] = Math.floor(2 + Math.random() * 8);
    });
    data.push(entry);
  }
  return { data, departments };
}

function generateWaitTimeByHour() {
  const data = [];
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 60 * 60 * 1000);
    const timeOfDay = hour.getHours();
    // Longer waits during busy hours
    const baseFactor = timeOfDay >= 10 && timeOfDay <= 18 ? 1.4 : 0.8;
    data.push({
      hour: hour.getHours().toString().padStart(2, "0") + ":00",
      avgWait: Math.floor((15 + Math.random() * 20) * baseFactor),
      critical: Math.floor((5 + Math.random() * 8) * baseFactor),
      minor: Math.floor((25 + Math.random() * 30) * baseFactor),
    });
  }
  return data;
}

function generateConfidenceTrend() {
  const data = [];
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 60 * 60 * 1000);
    data.push({
      hour: hour.getHours().toString().padStart(2, "0") + ":00",
      confidence: Math.floor(78 + Math.random() * 15),
      overrideRate: Math.floor(2 + Math.random() * 6),
    });
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
      { esi: 1, count: 0, label: "Resuscitation", color: "#dc2626" },
      { esi: 2, count: 0, label: "Emergent", color: "#ea580c" },
      { esi: 3, count: 0, label: "Urgent", color: "#d97706" },
      { esi: 4, count: 0, label: "Less Urgent", color: "#84cc16" },
      { esi: 5, count: 0, label: "Non-Urgent", color: "#22c55e" },
    ],
    byDepartment: {} as Record<string, { total: number; critical: number; avgConf: number }>,
    byArrival: [
      { mode: "Ambulance", count: 0, color: "#ef4444" },
      { mode: "Walk-in", count: 0, color: "#64748b" },
      { mode: "Referral", count: 0, color: "#0d9488" },
    ],
    riskDistribution: [
      { name: "Critical", value: 0, color: "#dc2626" },
      { name: "Urgent", value: 0, color: "#f59e0b" },
      { name: "Minor", value: 0, color: "#22c55e" },
    ],
  };

  let totalConf = 0;

  patients.forEach(p => {
    // Acuity
    if (p.aiDecision.acuityColor === "critical") {
      stats.critical++;
      stats.riskDistribution[0].value++;
    } else if (p.aiDecision.acuityColor === "urgent") {
      stats.urgent++;
      stats.riskDistribution[1].value++;
    } else {
      stats.minor++;
      stats.riskDistribution[2].value++;
    }

    // ESI
    const esiIdx = p.aiDecision.esi - 1;
    if (esiIdx >= 0 && esiIdx < 5) stats.byESI[esiIdx].count++;

    // Confidence
    totalConf += p.aiDecision.confidence;

    // Department
    const dept = p.aiDecision.specialists[0] || "General";
    if (!stats.byDepartment[dept]) {
      stats.byDepartment[dept] = { total: 0, critical: 0, avgConf: 0 };
    }
    stats.byDepartment[dept].total++;
    if (p.aiDecision.esi <= 2) stats.byDepartment[dept].critical++;
    stats.byDepartment[dept].avgConf += p.aiDecision.confidence;

    // Arrival mode
    const arrivalIdx = stats.byArrival.findIndex(a => a.mode === p.arrivalMode);
    if (arrivalIdx >= 0) stats.byArrival[arrivalIdx].count++;
  });

  // Finalize averages
  Object.values(stats.byDepartment).forEach(d => {
    d.avgConf = Math.round(d.avgConf / d.total);
  });
  stats.avgConfidence = Math.round(totalConf / patients.length);

  return stats;
}

// ============================================
// COMPONENTS
// ============================================

function KPICard({ label, value, subtext, trend, icon: Icon, color = "text-slate-900" }: {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: { direction: "up" | "down"; value: string; good?: boolean };
  icon?: React.ElementType;
  color?: string;
}) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 p-3 flex items-center gap-3">
      {Icon && (
        <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
          <Icon className="w-4 h-4 text-slate-500" />
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-slate-500 uppercase tracking-wide truncate">{label}</div>
        <div className={cn("text-xl font-bold font-mono tabular-nums", color)}>{value}</div>
        {subtext && <div className="text-[10px] text-slate-400">{subtext}</div>}
      </div>
      {trend && (
        <div className={cn(
          "text-[10px] flex items-center gap-0.5",
          trend.good ? "text-emerald-600" : "text-red-500"
        )}>
          {trend.direction === "up" ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
          {trend.value}
        </div>
      )}
    </div>
  );
}

function ChartCard({ title, children, className }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 flex flex-col", className)}>
      <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">{title}</span>
      </div>
      <div className="flex-1 p-3">
        {children}
      </div>
    </div>
  );
}

const CHART_COLORS = {
  teal: "#0d9488",
  red: "#ef4444",
  amber: "#f59e0b",
  emerald: "#22c55e",
  blue: "#3b82f6",
  purple: "#8b5cf6",
  slate: "#64748b",
};

// ============================================
// MAIN DASHBOARD
// ============================================

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  const stats = useMemo(() => computeStats(mockPatients), []);
  const hourlyFlow = useMemo(() => generateHourlyFlow(), []);
  const deptTimeSeries = useMemo(() => generateDepartmentTimeSeries(), []);
  const waitTimeTrend = useMemo(() => generateWaitTimeByHour(), []);
  const confidenceTrend = useMemo(() => generateConfidenceTrend(), []);

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
    return <div className="min-h-screen bg-slate-100 dark:bg-slate-950" />;
  }

  const timeStr = currentTime.toLocaleTimeString("en-US", { hour12: false });
  const dateStr = currentTime.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-[#0a0f1a] text-slate-900 dark:text-slate-100">
      {/* HEADER */}
      <header className="h-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-3 text-xs">
        <div className="flex items-center gap-4">
          <Link href="/" className="font-semibold text-slate-700 dark:text-slate-200 hover:text-teal-600">
            Patient.ly
          </Link>
          <span className="text-slate-400">|</span>
          <span className="text-slate-500">Operations Dashboard</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-slate-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] uppercase tracking-wider">Live</span>
          </div>
          <span className="text-slate-400 font-mono">{dateStr}</span>
          <span className="text-slate-700 dark:text-slate-300 font-mono font-medium">{timeStr}</span>
          <Link href="/queue" className="ml-2 px-2.5 py-1 bg-slate-800 text-white text-[10px] uppercase tracking-wide rounded hover:bg-slate-700 flex items-center gap-1">
            Queue <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <div className="p-3 space-y-3">

        {/* ROW 1: KPI Cards */}
        <div className="grid grid-cols-6 gap-3">
          <KPICard label="Total Census" value={stats.total} icon={Users} trend={{ direction: "up", value: "+8%", good: true }} />
          <KPICard label="Critical" value={stats.critical} icon={AlertTriangle} color="text-red-600" subtext={`${Math.round(stats.critical / stats.total * 100)}% of total`} />
          <KPICard label="Pending Review" value={stats.pendingReview} icon={Clock} color="text-amber-600" />
          <KPICard label="Avg Wait Time" value={`${stats.avgWaitTime}m`} trend={{ direction: "down", value: "-12%", good: true }} />
          <KPICard label="AI Confidence" value={`${stats.avgConfidence}%`} icon={Zap} color="text-teal-600" />
          <KPICard label="Throughput (12h)" value={hourlyFlow.slice(-12).reduce((s, h) => s + h.discharged, 0)} icon={TrendingUp} color="text-emerald-600" />
        </div>

        {/* ROW 2: Main Charts */}
        <div className="grid grid-cols-12 gap-3">
          {/* Patient Flow - Large Area Chart */}
          <ChartCard title="Patient Flow (24h) — Arrivals vs Discharges" className="col-span-8 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={hourlyFlow}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={2} />
                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }}
                  labelStyle={{ fontWeight: 600 }}
                />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Area type="monotone" dataKey="arrivals" fill="#0d9488" fillOpacity={0.3} stroke="#0d9488" strokeWidth={2} name="Arrivals" />
                <Area type="monotone" dataKey="discharged" fill="#3b82f6" fillOpacity={0.2} stroke="#3b82f6" strokeWidth={2} name="Discharged" />
                <Line type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2} dot={false} name="Critical" />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* ESI Distribution - Bar Chart */}
          <ChartCard title="ESI Level Distribution" className="col-span-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.byESI} layout="vertical" barSize={20}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={true} vertical={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis type="category" dataKey="label" tick={{ fontSize: 10, fill: '#64748b' }} width={80} />
                <Tooltip
                  contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {stats.byESI.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ROW 3: Department & Risk */}
        <div className="grid grid-cols-12 gap-3">
          {/* Department Load Over Time - Stacked Area */}
          <ChartCard title="Department Load Over Time (12h)" className="col-span-6 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={deptTimeSeries.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Area type="monotone" dataKey="Cardiology" stackId="1" fill="#ef4444" stroke="#ef4444" fillOpacity={0.6} />
                <Area type="monotone" dataKey="Neurology" stackId="1" fill="#f59e0b" stroke="#f59e0b" fillOpacity={0.6} />
                <Area type="monotone" dataKey="Orthopedics" stackId="1" fill="#22c55e" stroke="#22c55e" fillOpacity={0.6} />
                <Area type="monotone" dataKey="Pulmonology" stackId="1" fill="#3b82f6" stroke="#3b82f6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="General" stackId="1" fill="#8b5cf6" stroke="#8b5cf6" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Risk Distribution Pie */}
          <ChartCard title="Risk Distribution" className="col-span-3 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.riskDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {stats.riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Arrival Mode Pie */}
          <ChartCard title="Arrival Mode" className="col-span-3 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.byArrival}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={3}
                  dataKey="count"
                  label={({ mode, percent }) => `${mode} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {stats.byArrival.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ROW 4: Wait Times & AI Performance */}
        <div className="grid grid-cols-12 gap-3">
          {/* Wait Time Trends */}
          <ChartCard title="Wait Time Trends (24h) — By Acuity Level" className="col-span-6 h-52">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={waitTimeTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={3} />
                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} unit="m" />
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Line type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2} dot={false} name="Critical" />
                <Line type="monotone" dataKey="avgWait" stroke="#f59e0b" strokeWidth={2} dot={false} name="Average" />
                <Line type="monotone" dataKey="minor" stroke="#22c55e" strokeWidth={2} dot={false} name="Minor" />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* AI Confidence & Override Trend */}
          <ChartCard title="AI Performance (24h) — Confidence & Override Rate" className="col-span-6 h-52">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={confidenceTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={3} />
                <YAxis yAxisId="left" tick={{ fontSize: 10, fill: '#94a3b8' }} domain={[70, 100]} unit="%" />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#94a3b8' }} domain={[0, 15]} unit="%" />
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e2e8f0' }} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Area yAxisId="left" type="monotone" dataKey="confidence" fill="#0d9488" fillOpacity={0.3} stroke="#0d9488" strokeWidth={2} name="Confidence %" />
                <Line yAxisId="right" type="monotone" dataKey="overrideRate" stroke="#ef4444" strokeWidth={2} dot={false} name="Override Rate %" />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ROW 5: Department Table & Recent Activity */}
        <div className="grid grid-cols-12 gap-3">
          {/* Department Stats Table */}
          <div className="col-span-5 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Department Overview</span>
              <span className="text-[10px] text-slate-400">{departmentList.length} active</span>
            </div>
            <div className="overflow-auto max-h-48">
              <table className="w-full text-[11px]">
                <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/80">
                  <tr className="text-slate-500">
                    <th className="text-left py-1.5 px-3 font-medium">Department</th>
                    <th className="text-center py-1.5 px-2 font-medium">Total</th>
                    <th className="text-center py-1.5 px-2 font-medium">Critical</th>
                    <th className="text-center py-1.5 px-2 font-medium">Confidence</th>
                    <th className="text-left py-1.5 px-2 font-medium">Load</th>
                  </tr>
                </thead>
                <tbody>
                  {departmentList.map((dept, idx) => (
                    <tr key={dept.name} className={cn("border-t border-slate-50 dark:border-slate-800/50", idx % 2 === 1 && "bg-slate-50/50 dark:bg-slate-800/20")}>
                      <td className="py-1.5 px-3 font-medium text-slate-700 dark:text-slate-200">{dept.name}</td>
                      <td className="py-1.5 px-2 text-center font-mono tabular-nums">{dept.total}</td>
                      <td className="py-1.5 px-2 text-center">
                        {dept.critical > 0 ? (
                          <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] rounded text-[10px] font-semibold bg-red-100 text-red-700">{dept.critical}</span>
                        ) : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="py-1.5 px-2 text-center">
                        <span className={cn("font-mono tabular-nums font-medium", dept.avgConf >= 85 ? "text-emerald-600" : dept.avgConf >= 75 ? "text-amber-600" : "text-red-500")}>
                          {dept.avgConf}%
                        </span>
                      </td>
                      <td className="py-1.5 px-2">
                        <div className="h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden w-16">
                          <div
                            className={cn("h-full rounded-full", dept.critical > 2 ? "bg-red-500" : dept.critical > 0 ? "bg-amber-500" : "bg-teal-500")}
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
          <div className="col-span-7 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
            <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Recent Triage Activity</span>
              <Link href="/queue" className="text-[10px] text-teal-600 hover:text-teal-700 flex items-center gap-0.5">
                View All <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="overflow-auto max-h-48">
              <table className="w-full text-[11px]">
                <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/80">
                  <tr className="text-slate-500">
                    <th className="text-left py-1.5 px-3 font-medium">Patient</th>
                    <th className="text-left py-1.5 px-2 font-medium">Complaint</th>
                    <th className="text-center py-1.5 px-2 font-medium">ESI</th>
                    <th className="text-center py-1.5 px-2 font-medium">Conf</th>
                    <th className="text-left py-1.5 px-2 font-medium">Dept</th>
                    <th className="text-right py-1.5 px-3 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {mockPatients.slice(0, 10).map((patient, idx) => (
                    <tr key={patient.id} className={cn("border-t border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/30 cursor-pointer", idx % 2 === 1 && "bg-slate-50/50 dark:bg-slate-800/20")}>
                      <td className="py-1.5 px-3">
                        <div className="flex items-center gap-1.5">
                          <span className={cn("w-1.5 h-1.5 rounded-full", patient.aiDecision.acuityColor === "critical" ? "bg-red-500" : patient.aiDecision.acuityColor === "urgent" ? "bg-amber-500" : "bg-emerald-500")} />
                          <span className="font-medium text-slate-700 dark:text-slate-200">{patient.name}</span>
                          <span className="text-slate-400 text-[10px]">{patient.age}{patient.gender}</span>
                        </div>
                      </td>
                      <td className="py-1.5 px-2 text-slate-500 truncate max-w-[150px]">{patient.chiefComplaint}</td>
                      <td className="py-1.5 px-2 text-center">
                        <span className={cn(
                          "inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-bold text-white",
                          patient.aiDecision.esi === 1 ? "bg-red-600" : patient.aiDecision.esi === 2 ? "bg-orange-500" : patient.aiDecision.esi === 3 ? "bg-amber-500" : patient.aiDecision.esi === 4 ? "bg-lime-500" : "bg-emerald-500"
                        )}>
                          {patient.aiDecision.esi}
                        </span>
                      </td>
                      <td className="py-1.5 px-2 text-center">
                        <span className={cn("font-mono tabular-nums font-medium", patient.aiDecision.confidence >= 85 ? "text-emerald-600" : patient.aiDecision.confidence >= 75 ? "text-amber-600" : "text-red-500")}>
                          {patient.aiDecision.confidence}%
                        </span>
                      </td>
                      <td className="py-1.5 px-2 text-slate-500 truncate max-w-[80px]">{patient.aiDecision.specialists[0] || "—"}</td>
                      <td className="py-1.5 px-3 text-right text-slate-400 text-[10px] font-mono">{patient.arrivalTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
