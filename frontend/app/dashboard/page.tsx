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
  BarChart3,
  ArrowLeft,
  CheckCircle2,
  Timer,
  Gauge,
  MessageSquare,
  ShieldAlert,
  Building2,
  PieChart,
  Zap,
  Target,
  Layers,
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ComposedChart,
  Line,
  ScatterChart,
  Scatter,
  ZAxis,
  Treemap,
  PieChart as RechartsPieChart,
  Pie,
} from "recharts";

// Generate simulated hourly data
function generateHourlyData() {
  const hours = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hourLabel = hour.getHours().toString().padStart(2, "0") + ":00";
    const baseArrivals = 3 + Math.sin((hour.getHours() - 6) * Math.PI / 12) * 2;
    const arrivals = Math.max(1, Math.round(baseArrivals + Math.random() * 3));
    const triaged = Math.round(arrivals * (0.85 + Math.random() * 0.15));
    const highRisk = Math.round(arrivals * (0.15 + Math.random() * 0.1));
    hours.push({ hour: hourLabel, arrivals, triaged, highRisk, pending: arrivals - triaged });
  }
  return hours;
}

// Compute comprehensive stats
function computeStats(patients: Patient[]) {
  const stats = {
    total: patients.length,
    byESI: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 } as Record<number, number>,
    byAcuity: { critical: 0, urgent: 0, minor: 0 },
    byDepartment: {} as Record<string, { count: number; highRisk: number; avgConfidence: number; patients: Patient[] }>,
    avgConfidence: 0,
    highRisk: 0,
    mediumRisk: 0,
    lowRisk: 0,
    byArrivalMode: { Ambulance: 0, "Walk-in": 0, Referral: 0 } as Record<string, number>,
  };

  let totalConfidence = 0;

  patients.forEach((p) => {
    stats.byESI[p.aiDecision.esi]++;
    stats.byAcuity[p.aiDecision.acuityColor]++;
    stats.byArrivalMode[p.arrivalMode]++;
    totalConfidence += p.aiDecision.confidence;

    if (p.aiDecision.esi <= 2) stats.highRisk++;
    else if (p.aiDecision.esi === 3) stats.mediumRisk++;
    else stats.lowRisk++;

    // Department stats
    p.aiDecision.specialists.forEach((spec) => {
      if (!stats.byDepartment[spec]) {
        stats.byDepartment[spec] = { count: 0, highRisk: 0, avgConfidence: 0, patients: [] };
      }
      stats.byDepartment[spec].count++;
      stats.byDepartment[spec].patients.push(p);
      if (p.aiDecision.esi <= 2) stats.byDepartment[spec].highRisk++;
    });
  });

  // Calculate department avg confidence
  Object.keys(stats.byDepartment).forEach(dept => {
    const deptPatients = stats.byDepartment[dept].patients;
    stats.byDepartment[dept].avgConfidence = Math.round(
      deptPatients.reduce((sum, p) => sum + p.aiDecision.confidence, 0) / deptPatients.length
    );
  });

  stats.avgConfidence = Math.round(totalConfidence / patients.length);
  return stats;
}

// Compute confidence distribution
function computeConfidenceDistribution(patients: Patient[]) {
  const buckets = [
    { range: "60-70%", min: 60, max: 70, count: 0, color: "#ef4444" },
    { range: "70-75%", min: 70, max: 75, count: 0, color: "#f97316" },
    { range: "75-80%", min: 75, max: 80, count: 0, color: "#eab308" },
    { range: "80-85%", min: 80, max: 85, count: 0, color: "#84cc16" },
    { range: "85-90%", min: 85, max: 90, count: 0, color: "#22c55e" },
    { range: "90-95%", min: 90, max: 95, count: 0, color: "#10b981" },
    { range: "95-100%", min: 95, max: 100, count: 0, color: "#059669" },
  ];

  patients.forEach(p => {
    const conf = p.aiDecision.confidence;
    const bucket = buckets.find(b => conf >= b.min && conf < b.max);
    if (bucket) bucket.count++;
    else if (conf === 100) buckets[buckets.length - 1].count++;
  });

  return buckets;
}

// Compute vitals radar
function computeVitalsRadar(patients: Patient[]) {
  const riskGroups = {
    high: { patients: [] as Patient[] },
    medium: { patients: [] as Patient[] },
    low: { patients: [] as Patient[] },
  };

  patients.forEach(p => {
    if (p.aiDecision.esi <= 2) riskGroups.high.patients.push(p);
    else if (p.aiDecision.esi === 3) riskGroups.medium.patients.push(p);
    else riskGroups.low.patients.push(p);
  });

  const calcAvg = (group: Patient[], getter: (p: Patient) => number) => {
    if (group.length === 0) return 0;
    return group.reduce((sum, p) => sum + getter(p), 0) / group.length;
  };

  const normalize = (value: number, min: number, max: number) =>
    Math.round(((value - min) / (max - min)) * 100);

  const metrics = [
    { metric: "Heart Rate" },
    { metric: "BP Systolic" },
    { metric: "SpO2" },
    { metric: "Temperature" },
    { metric: "Resp Rate" },
  ];

  return metrics.map(m => {
    const getVital = (p: Patient): number => {
      switch (m.metric) {
        case "Heart Rate": return typeof p.vitals.hr.value === 'number' ? p.vitals.hr.value : 80;
        case "BP Systolic": return parseInt(String(p.vitals.bp.value).split('/')[0]) || 120;
        case "SpO2": return typeof p.vitals.spo2.value === 'number' ? p.vitals.spo2.value : 98;
        case "Temperature": return typeof p.vitals.temp.value === 'number' ? p.vitals.temp.value : 98.6;
        case "Resp Rate": return typeof p.vitals.rr.value === 'number' ? p.vitals.rr.value : 16;
        default: return 0;
      }
    };

    const getNormalized = (value: number): number => {
      switch (m.metric) {
        case "Heart Rate": return normalize(value, 40, 180);
        case "BP Systolic": return normalize(value, 70, 200);
        case "SpO2": return normalize(value, 80, 100);
        case "Temperature": return normalize(value, 95, 105);
        case "Resp Rate": return normalize(value, 8, 40);
        default: return 50;
      }
    };

    return {
      metric: m.metric,
      high: getNormalized(calcAvg(riskGroups.high.patients, getVital)),
      medium: getNormalized(calcAvg(riskGroups.medium.patients, getVital)),
      low: getNormalized(calcAvg(riskGroups.low.patients, getVital)),
      fullMark: 100,
    };
  });
}

// Compute complaint frequency
function computeComplaintFrequency(patients: Patient[]) {
  const wordCounts: Record<string, number> = {};
  const stopWords = new Set(['and', 'the', 'with', 'for', 'from', 'has', 'been', 'was', 'are', 'is', 'of', 'to', 'in', 'on', 'a', 'an']);

  patients.forEach(p => {
    const words = p.chiefComplaint.toLowerCase()
      .replace(/[^a-z\s]/g, '')
      .split(/\s+/)
      .filter(w => w.length > 2 && !stopWords.has(w));
    words.forEach(word => {
      wordCounts[word] = (wordCounts[word] || 0) + 1;
    });
  });

  return Object.entries(wordCounts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);
}

// Section header component
function SectionHeader({ icon: Icon, title, subtitle }: { icon: React.ElementType; title: string; subtitle?: string }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-3 mb-1">
        <div className="p-2 rounded-lg bg-teal-100 dark:bg-teal-900/30">
          <Icon className="h-5 w-5 text-teal-600 dark:text-teal-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">{title}</h2>
      </div>
      {subtitle && <p className="text-sm text-slate-500 ml-12">{subtitle}</p>}
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

// Treemap content
const TreemapContent = (props: { x: number; y: number; width: number; height: number; name: string; value: number }) => {
  const { x, y, width, height, name, value } = props;
  if (width < 40 || height < 30) return null;
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} fill="rgb(20, 184, 166)" fillOpacity={0.3 + (value / 20) * 0.5} stroke="white" strokeWidth={2} rx={4} />
      <text x={x + width / 2} y={y + height / 2 - 6} textAnchor="middle" fill="#0f766e" fontSize={Math.min(14, width / 6)} fontWeight="600">{name}</text>
      <text x={x + width / 2} y={y + height / 2 + 10} textAnchor="middle" fill="#0f766e" fontSize={Math.min(12, width / 8)}>{value}</text>
    </g>
  );
};

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);

  const stats = useMemo(() => computeStats(mockPatients), []);
  const hourlyData = useMemo(() => generateHourlyData(), []);
  const confidenceDistribution = useMemo(() => computeConfidenceDistribution(mockPatients), []);
  const vitalsRadar = useMemo(() => computeVitalsRadar(mockPatients), []);
  const complaintFrequency = useMemo(() => computeComplaintFrequency(mockPatients), []);

  // Risk pie chart data
  const riskPieData = [
    { name: "High Risk", value: stats.highRisk, color: "#ef4444" },
    { name: "Medium Risk", value: stats.mediumRisk, color: "#f59e0b" },
    { name: "Low Risk", value: stats.lowRisk, color: "#10b981" },
  ];

  // ESI bar data
  const esiBarData = [
    { name: "ESI-1", value: stats.byESI[1], color: "#dc2626", label: "Resuscitation" },
    { name: "ESI-2", value: stats.byESI[2], color: "#ea580c", label: "Emergent" },
    { name: "ESI-3", value: stats.byESI[3], color: "#d97706", label: "Urgent" },
    { name: "ESI-4", value: stats.byESI[4], color: "#65a30d", label: "Less Urgent" },
    { name: "ESI-5", value: stats.byESI[5], color: "#16a34a", label: "Non-Urgent" },
  ];

  // Department data sorted by count
  const departmentData = Object.entries(stats.byDepartment)
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.count - a.count);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="min-h-screen bg-slate-50 dark:bg-slate-950" />;
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="p-1.5 -ml-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800">
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </Link>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-teal-600" />
              <span className="font-semibold text-slate-900 dark:text-slate-100">Analytics Dashboard</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live</span>
            </div>
            <Link href="/queue" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 transition-colors">
              Open Queue <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-12">

        {/* ============================================ */}
        {/* SECTION 1: RISK SUMMARY                     */}
        {/* ============================================ */}
        <section>
          <SectionHeader
            icon={ShieldAlert}
            title="Risk Summary"
            subtitle="Patient classification by risk level and ESI scores"
          />

          {/* Key Metrics Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5">
              <p className="text-sm text-slate-500 mb-1">Total Patients</p>
              <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">
                <AnimatedCounter value={stats.total} />
              </p>
              <div className="flex items-center gap-1 mt-2 text-xs text-emerald-600">
                <TrendingUp className="h-3 w-3" />
                <span>+12% vs last hour</span>
              </div>
            </div>
            <div className="rounded-xl border-2 border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-900/20 p-5">
              <p className="text-sm text-red-700 dark:text-red-300 mb-1">High Risk (ESI 1-2)</p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                <AnimatedCounter value={stats.highRisk} />
              </p>
              <p className="text-xs text-red-600/70 mt-2">
                {Math.round((stats.highRisk / stats.total) * 100)}% of total
              </p>
            </div>
            <div className="rounded-xl border-2 border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-900/20 p-5">
              <p className="text-sm text-amber-700 dark:text-amber-300 mb-1">Medium Risk (ESI 3)</p>
              <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">
                <AnimatedCounter value={stats.mediumRisk} />
              </p>
              <p className="text-xs text-amber-600/70 mt-2">
                {Math.round((stats.mediumRisk / stats.total) * 100)}% of total
              </p>
            </div>
            <div className="rounded-xl border-2 border-emerald-200 dark:border-emerald-900/50 bg-emerald-50 dark:bg-emerald-900/20 p-5">
              <p className="text-sm text-emerald-700 dark:text-emerald-300 mb-1">Low Risk (ESI 4-5)</p>
              <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
                <AnimatedCounter value={stats.lowRisk} />
              </p>
              <p className="text-xs text-emerald-600/70 mt-2">
                {Math.round((stats.lowRisk / stats.total) * 100)}% of total
              </p>
            </div>
          </div>

          {/* Risk Distribution Charts */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Risk Level Pie Chart */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <PieChart className="h-4 w-4 text-slate-400" />
                Risk Level Distribution
              </h3>
              <div className="h-64 flex items-center">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={riskPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {riskPieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg p-3">
                              <p className="font-medium">{payload[0].name}</p>
                              <p className="text-sm">{payload[0].value} patients</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* ESI Level Breakdown */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Layers className="h-4 w-4 text-slate-400" />
                ESI Level Breakdown
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={esiBarData} layout="vertical" barSize={24}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={true} vertical={false} />
                    <XAxis type="number" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} width={50} />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg p-3">
                              <p className="font-medium">{data.name}: {data.label}</p>
                              <p className="text-sm">{data.value} patients</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {esiBarData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Acuity Details */}
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="rounded-lg border border-red-200 dark:border-red-900/50 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-900/10 p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold text-red-800 dark:text-red-300">Critical</span>
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <p className="text-4xl font-bold text-red-700 dark:text-red-400 mb-1">{stats.byAcuity.critical}</p>
              <p className="text-xs text-red-600/80">Life-threatening • Immediate care required</p>
            </div>
            <div className="rounded-lg border border-amber-200 dark:border-amber-900/50 bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-900/10 p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold text-amber-800 dark:text-amber-300">Urgent</span>
                <Clock className="h-5 w-5 text-amber-600" />
              </div>
              <p className="text-4xl font-bold text-amber-700 dark:text-amber-400 mb-1">{stats.byAcuity.urgent}</p>
              <p className="text-xs text-amber-600/80">Time-sensitive • Priority attention</p>
            </div>
            <div className="rounded-lg border border-emerald-200 dark:border-emerald-900/50 bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-900/10 p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">Minor</span>
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              </div>
              <p className="text-4xl font-bold text-emerald-700 dark:text-emerald-400 mb-1">{stats.byAcuity.minor}</p>
              <p className="text-xs text-emerald-600/80">Non-urgent • Standard queue</p>
            </div>
          </div>
        </section>

        {/* ============================================ */}
        {/* SECTION 2: VISUALIZATIONS                   */}
        {/* ============================================ */}
        <section>
          <SectionHeader
            icon={BarChart3}
            title="Visualizations"
            subtitle="Real-time analytics and trends"
          />

          {/* Row 1: Patient Flow + Confidence */}
          <div className="grid lg:grid-cols-2 gap-6 mb-6">
            {/* Patient Flow */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-900 dark:text-slate-100">Patient Flow (24h)</h3>
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-teal-500" />
                    <span className="text-slate-500">Arrivals</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                    <span className="text-slate-500">High Risk</span>
                  </div>
                </div>
              </div>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={3} />
                    <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <Tooltip />
                    <Area type="monotone" dataKey="arrivals" fill="rgb(20, 184, 166)" fillOpacity={0.2} stroke="rgb(20, 184, 166)" strokeWidth={2} name="Arrivals" />
                    <Line type="monotone" dataKey="highRisk" stroke="rgb(239, 68, 68)" strokeWidth={2} dot={false} name="High Risk" />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Confidence Distribution */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Brain className="h-4 w-4 text-slate-400" />
                AI Confidence Distribution
              </h3>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={confidenceDistribution} barCategoryGap="15%">
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="range" tick={{ fontSize: 9, fill: '#94a3b8' }} />
                    <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <Tooltip />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Patients">
                      {confidenceDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Row 2: Vitals Radar + Complaint Treemap */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Vitals Radar */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Heart className="h-4 w-4 text-slate-400" />
                Vitals by Risk Level
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={vitalsRadar}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9, fill: '#94a3b8' }} />
                    <Radar name="High Risk" dataKey="high" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} strokeWidth={2} />
                    <Radar name="Medium" dataKey="medium" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} strokeWidth={2} />
                    <Radar name="Low Risk" dataKey="low" stroke="#10b981" fill="#10b981" fillOpacity={0.2} strokeWidth={2} />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Complaint Treemap */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-slate-400" />
                Chief Complaint Keywords
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <Treemap data={complaintFrequency} dataKey="value" aspectRatio={4 / 3} stroke="#fff" content={<TreemapContent x={0} y={0} width={0} height={0} name="" value={0} />} />
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </section>

        {/* ============================================ */}
        {/* SECTION 3: DEPARTMENT INSIGHTS              */}
        {/* ============================================ */}
        <section>
          <SectionHeader
            icon={Building2}
            title="Department Insights"
            subtitle="Patient distribution and workload analysis by department"
          />

          {/* Department Stats Table */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden mb-6">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/50">
                    <th className="text-left py-4 px-6 text-sm font-semibold text-slate-700 dark:text-slate-300">Department</th>
                    <th className="text-center py-4 px-6 text-sm font-semibold text-slate-700 dark:text-slate-300">Total Patients</th>
                    <th className="text-center py-4 px-6 text-sm font-semibold text-slate-700 dark:text-slate-300">High Risk</th>
                    <th className="text-center py-4 px-6 text-sm font-semibold text-slate-700 dark:text-slate-300">% High Risk</th>
                    <th className="text-center py-4 px-6 text-sm font-semibold text-slate-700 dark:text-slate-300">Avg. Confidence</th>
                    <th className="text-left py-4 px-6 text-sm font-semibold text-slate-700 dark:text-slate-300">Workload</th>
                  </tr>
                </thead>
                <tbody>
                  {departmentData.slice(0, 8).map((dept, idx) => {
                    const highRiskPct = Math.round((dept.highRisk / dept.count) * 100);
                    const workloadPct = Math.round((dept.count / stats.total) * 100);
                    return (
                      <tr key={dept.name} className={cn("border-t border-slate-100 dark:border-slate-800", idx % 2 === 0 ? "" : "bg-slate-50/50 dark:bg-slate-800/20")}>
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-teal-100 dark:bg-teal-900/30">
                              <Stethoscope className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                            </div>
                            <span className="font-medium text-slate-900 dark:text-slate-100">{dept.name}</span>
                          </div>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">{dept.count}</span>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <span className={cn("inline-flex items-center justify-center h-7 min-w-[2rem] px-2 rounded-full text-sm font-semibold", dept.highRisk > 0 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" : "bg-slate-100 text-slate-500 dark:bg-slate-800")}>
                            {dept.highRisk}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <span className={cn("text-sm font-medium", highRiskPct >= 30 ? "text-red-600" : highRiskPct >= 15 ? "text-amber-600" : "text-emerald-600")}>
                            {highRiskPct}%
                          </span>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <span className={cn("text-sm font-semibold", dept.avgConfidence >= 85 ? "text-emerald-600" : dept.avgConfidence >= 75 ? "text-amber-600" : "text-red-600")}>
                            {dept.avgConfidence}%
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                              <div className="h-full bg-teal-500 rounded-full transition-all" style={{ width: `${workloadPct}%` }} />
                            </div>
                            <span className="text-xs text-slate-500 w-8">{workloadPct}%</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Department Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-4 w-4 text-teal-600" />
                <span className="text-sm text-slate-500">Top Department</span>
              </div>
              <p className="font-semibold text-slate-900 dark:text-slate-100">{departmentData[0]?.name || "N/A"}</p>
              <p className="text-xs text-slate-400">{departmentData[0]?.count || 0} patients</p>
            </div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <span className="text-sm text-slate-500">Highest Risk</span>
              </div>
              <p className="font-semibold text-slate-900 dark:text-slate-100">
                {departmentData.sort((a, b) => (b.highRisk / b.count) - (a.highRisk / a.count))[0]?.name || "N/A"}
              </p>
              <p className="text-xs text-slate-400">
                {Math.round((departmentData[0]?.highRisk / departmentData[0]?.count) * 100) || 0}% high risk
              </p>
            </div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-violet-600" />
                <span className="text-sm text-slate-500">Best AI Confidence</span>
              </div>
              <p className="font-semibold text-slate-900 dark:text-slate-100">
                {departmentData.sort((a, b) => b.avgConfidence - a.avgConfidence)[0]?.name || "N/A"}
              </p>
              <p className="text-xs text-slate-400">
                {departmentData.sort((a, b) => b.avgConfidence - a.avgConfidence)[0]?.avgConfidence || 0}% avg
              </p>
            </div>
            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Users className="h-4 w-4 text-amber-600" />
                <span className="text-sm text-slate-500">Total Departments</span>
              </div>
              <p className="font-semibold text-slate-900 dark:text-slate-100">{departmentData.length}</p>
              <p className="text-xs text-slate-400">Active today</p>
            </div>
          </div>
        </section>

        {/* ============================================ */}
        {/* SECTION 4: RECENT ACTIVITY                  */}
        {/* ============================================ */}
        <section>
          <SectionHeader
            icon={Activity}
            title="Recent Triage Decisions"
            subtitle="Latest patient triage outcomes"
          />

          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/50">
                    <th className="text-left py-3 px-4 font-medium text-slate-500">Patient</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500">Chief Complaint</th>
                    <th className="text-center py-3 px-4 font-medium text-slate-500">Risk</th>
                    <th className="text-center py-3 px-4 font-medium text-slate-500">ESI</th>
                    <th className="text-center py-3 px-4 font-medium text-slate-500">Confidence</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500">Department</th>
                    <th className="text-right py-3 px-4 font-medium text-slate-500">Arrived</th>
                  </tr>
                </thead>
                <tbody>
                  {mockPatients.slice(0, 8).map((patient) => (
                    <tr key={patient.id} className="border-t border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-3 px-4">
                        <span className="font-medium text-slate-900 dark:text-slate-100">{patient.name}</span>
                        <span className="text-slate-400 ml-1 text-xs">{patient.age}{patient.gender}</span>
                      </td>
                      <td className="py-3 px-4 text-slate-600 dark:text-slate-400 max-w-48 truncate">{patient.chiefComplaint}</td>
                      <td className="py-3 px-4 text-center">
                        <span className={cn("inline-flex px-2 py-0.5 rounded-full text-xs font-medium", patient.aiDecision.esi <= 2 ? "bg-red-100 text-red-700" : patient.aiDecision.esi === 3 ? "bg-amber-100 text-amber-700" : "bg-emerald-100 text-emerald-700")}>
                          {patient.aiDecision.esi <= 2 ? "High" : patient.aiDecision.esi === 3 ? "Med" : "Low"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={cn("inline-flex h-6 w-6 items-center justify-center rounded text-white font-bold text-xs", patient.aiDecision.esi === 1 ? "bg-red-600" : patient.aiDecision.esi === 2 ? "bg-orange-500" : patient.aiDecision.esi === 3 ? "bg-amber-500" : patient.aiDecision.esi === 4 ? "bg-lime-500" : "bg-green-500")}>
                          {patient.aiDecision.esi}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={cn("font-semibold tabular-nums", patient.aiDecision.confidence >= 85 ? "text-emerald-600" : patient.aiDecision.confidence >= 70 ? "text-amber-600" : "text-red-600")}>
                          {patient.aiDecision.confidence}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600 dark:text-slate-400">{patient.aiDecision.specialists[0] || "—"}</td>
                      <td className="py-3 px-4 text-right text-slate-400 text-xs">{patient.arrivalTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="border-t border-slate-100 dark:border-slate-800 p-4 text-center">
              <Link href="/queue" className="text-sm text-teal-600 hover:text-teal-700 font-medium inline-flex items-center gap-1">
                View all patients <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
