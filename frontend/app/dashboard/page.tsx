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
} from "recharts";

// Generate simulated hourly data
function generateHourlyData() {
  const hours = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hourLabel = hour.getHours().toString().padStart(2, "0") + ":00";

    // Simulate realistic ED traffic patterns
    const baseArrivals = 3 + Math.sin((hour.getHours() - 6) * Math.PI / 12) * 2;
    const arrivals = Math.max(1, Math.round(baseArrivals + Math.random() * 3));
    const triaged = Math.round(arrivals * (0.85 + Math.random() * 0.15));
    const highRisk = Math.round(arrivals * (0.15 + Math.random() * 0.1));

    hours.push({
      hour: hourLabel,
      arrivals,
      triaged,
      highRisk,
      pending: arrivals - triaged,
    });
  }
  return hours;
}

// Generate department heatmap data
function generateDepartmentHeatmap() {
  const departments = ["Emergency", "Cardiology", "Neurology", "Orthopedics", "Internal Med", "Pediatrics"];
  const timeSlots = ["00-04", "04-08", "08-12", "12-16", "16-20", "20-24"];

  const data: { dept: string; time: string; value: number; }[] = [];

  departments.forEach(dept => {
    timeSlots.forEach(time => {
      // Simulate realistic patterns - busier during day
      const timeIndex = timeSlots.indexOf(time);
      const baseValue = timeIndex >= 2 && timeIndex <= 4 ? 8 : 4;
      const value = Math.round(baseValue + Math.random() * 6);
      data.push({ dept, time, value });
    });
  });

  return { data, departments, timeSlots };
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

// Compute vitals by risk level for radar chart
function computeVitalsRadar(patients: Patient[]) {
  const riskGroups = {
    high: { patients: [] as Patient[], label: "High Risk (ESI 1-2)" },
    medium: { patients: [] as Patient[], label: "Medium (ESI 3)" },
    low: { patients: [] as Patient[], label: "Low Risk (ESI 4-5)" },
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

  // Normalize vitals to 0-100 scale for radar
  const normalize = (value: number, min: number, max: number) =>
    Math.round(((value - min) / (max - min)) * 100);

  const metrics = [
    { metric: "Heart Rate", fullMark: 100 },
    { metric: "BP Systolic", fullMark: 100 },
    { metric: "SpO2", fullMark: 100 },
    { metric: "Temperature", fullMark: 100 },
    { metric: "Resp Rate", fullMark: 100 },
  ];

  return metrics.map(m => {
    const getVital = (p: Patient): number => {
      switch (m.metric) {
        case "Heart Rate": return typeof p.vitals.hr.value === 'number' ? p.vitals.hr.value : 80;
        case "BP Systolic": {
          const bp = String(p.vitals.bp.value);
          return parseInt(bp.split('/')[0]) || 120;
        }
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

// Compute chief complaint word frequency
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
    .slice(0, 15);
}

// ESI vs Confidence scatter data
function computeESIConfidenceScatter(patients: Patient[]) {
  return patients.map(p => ({
    esi: p.aiDecision.esi,
    confidence: p.aiDecision.confidence,
    name: p.name,
    complaint: p.chiefComplaint.slice(0, 30),
    size: p.aiDecision.esi <= 2 ? 100 : p.aiDecision.esi === 3 ? 60 : 40,
  }));
}

// Compute stats
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

// Custom tooltip for charts
function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg p-3">
        <p className="font-medium text-slate-900 dark:text-slate-100 mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: <span className="font-semibold">{entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
}

// Heatmap cell component
function HeatmapCell({ value, maxValue }: { value: number; maxValue: number }) {
  const intensity = value / maxValue;
  const bg = `rgba(20, 184, 166, ${0.1 + intensity * 0.8})`; // teal color

  return (
    <div
      className="h-10 w-full rounded flex items-center justify-center text-xs font-medium transition-all hover:scale-105"
      style={{
        backgroundColor: bg,
        color: intensity > 0.5 ? 'white' : 'rgb(15, 118, 110)',
      }}
    >
      {value}
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

// Treemap custom content
const TreemapContent = (props: { x: number; y: number; width: number; height: number; name: string; value: number }) => {
  const { x, y, width, height, name, value } = props;

  if (width < 40 || height < 30) return null;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill="rgb(20, 184, 166)"
        fillOpacity={0.3 + (value / 20) * 0.5}
        stroke="white"
        strokeWidth={2}
        rx={4}
      />
      <text
        x={x + width / 2}
        y={y + height / 2 - 6}
        textAnchor="middle"
        fill="#0f766e"
        fontSize={Math.min(14, width / 6)}
        fontWeight="600"
      >
        {name}
      </text>
      <text
        x={x + width / 2}
        y={y + height / 2 + 10}
        textAnchor="middle"
        fill="#0f766e"
        fontSize={Math.min(12, width / 8)}
      >
        {value}
      </text>
    </g>
  );
};

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false);

  const stats = useMemo(() => computeStats(mockPatients), []);
  const hourlyData = useMemo(() => generateHourlyData(), []);
  const heatmapData = useMemo(() => generateDepartmentHeatmap(), []);
  const confidenceDistribution = useMemo(() => computeConfidenceDistribution(mockPatients), []);
  const vitalsRadar = useMemo(() => computeVitalsRadar(mockPatients), []);
  const complaintFrequency = useMemo(() => computeComplaintFrequency(mockPatients), []);
  const esiConfidenceScatter = useMemo(() => computeESIConfidenceScatter(mockPatients), []);

  const heatmapMax = Math.max(...heatmapData.data.map(d => d.value));

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
            <Link
              href="/"
              className="p-1.5 -ml-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </Link>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-teal-600" />
              <span className="font-semibold text-slate-900 dark:text-slate-100">
                Analytics Dashboard
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
            value={<AnimatedCounter value={stats.total} />}
            subtitle="In system today"
            icon={Users}
            trend="up"
            trendValue="+12%"
            color="teal"
          />
          <SummaryCard
            title="High Risk (ESI 1-2)"
            value={<AnimatedCounter value={stats.highRisk} />}
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

        {/* Row 1: Patient Flow + Department Heatmap */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Hourly Patient Flow */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-slate-400" />
                <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                  Patient Flow (24h)
                </h2>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="h-2.5 w-2.5 rounded-full bg-teal-500" />
                  <span className="text-slate-500">Arrivals</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                  <span className="text-slate-500">Triaged</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                  <span className="text-slate-500">High Risk</span>
                </div>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="hour"
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    interval={2}
                  />
                  <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="arrivals"
                    fill="rgb(20, 184, 166)"
                    fillOpacity={0.2}
                    stroke="rgb(20, 184, 166)"
                    strokeWidth={2}
                    name="Arrivals"
                  />
                  <Line
                    type="monotone"
                    dataKey="triaged"
                    stroke="rgb(16, 185, 129)"
                    strokeWidth={2}
                    dot={false}
                    name="Triaged"
                  />
                  <Line
                    type="monotone"
                    dataKey="highRisk"
                    stroke="rgb(239, 68, 68)"
                    strokeWidth={2}
                    dot={false}
                    name="High Risk"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Department Heatmap */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <Stethoscope className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                Department Load Heatmap
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="text-left text-xs font-medium text-slate-400 pb-2 pr-2">Dept</th>
                    {heatmapData.timeSlots.map(time => (
                      <th key={time} className="text-center text-xs font-medium text-slate-400 pb-2 px-1 w-16">
                        {time}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {heatmapData.departments.map(dept => (
                    <tr key={dept}>
                      <td className="text-xs text-slate-600 dark:text-slate-400 pr-2 py-1 whitespace-nowrap">
                        {dept}
                      </td>
                      {heatmapData.timeSlots.map(time => {
                        const cell = heatmapData.data.find(d => d.dept === dept && d.time === time);
                        return (
                          <td key={time} className="px-1 py-1">
                            <HeatmapCell value={cell?.value || 0} maxValue={heatmapMax} />
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-end gap-2 mt-4">
              <span className="text-xs text-slate-400">Low</span>
              <div className="flex h-2 w-24 rounded overflow-hidden">
                {[0.1, 0.3, 0.5, 0.7, 0.9].map((opacity, i) => (
                  <div
                    key={i}
                    className="flex-1"
                    style={{ backgroundColor: `rgba(20, 184, 166, ${opacity})` }}
                  />
                ))}
              </div>
              <span className="text-xs text-slate-400">High</span>
            </div>
          </div>
        </div>

        {/* Row 2: Confidence Distribution + Vitals Radar */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* AI Confidence Distribution */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <Brain className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                AI Confidence Distribution
              </h2>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={confidenceDistribution} barCategoryGap="15%">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis
                    dataKey="range"
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    axisLine={false}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg p-3">
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {payload[0].payload.range}
                            </p>
                            <p className="text-sm text-slate-600">
                              {payload[0].value} patients
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {confidenceDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-slate-400 text-center mt-2">
              Distribution of AI confidence scores across all triage decisions
            </p>
          </div>

          {/* Vitals Radar Chart */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <Heart className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                Vitals by Risk Level
              </h2>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={vitalsRadar}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis
                    dataKey="metric"
                    tick={{ fontSize: 11, fill: '#64748b' }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={{ fontSize: 9, fill: '#94a3b8' }}
                  />
                  <Radar
                    name="High Risk"
                    dataKey="high"
                    stroke="#ef4444"
                    fill="#ef4444"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                  <Radar
                    name="Medium"
                    dataKey="medium"
                    stroke="#f59e0b"
                    fill="#f59e0b"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                  <Radar
                    name="Low Risk"
                    dataKey="low"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: 12 }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Row 3: ESI vs Confidence Scatter + Complaint Frequency */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* ESI vs Confidence Scatter Plot */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <Gauge className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                ESI Level vs AI Confidence
              </h2>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    type="number"
                    dataKey="esi"
                    name="ESI Level"
                    domain={[0.5, 5.5]}
                    ticks={[1, 2, 3, 4, 5]}
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    label={{ value: 'ESI Level', position: 'bottom', fontSize: 11, fill: '#64748b' }}
                  />
                  <YAxis
                    type="number"
                    dataKey="confidence"
                    name="Confidence"
                    domain={[60, 100]}
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    label={{ value: 'Confidence %', angle: -90, position: 'insideLeft', fontSize: 11, fill: '#64748b' }}
                  />
                  <ZAxis type="number" dataKey="size" range={[30, 120]} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg p-3">
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {data.name}
                            </p>
                            <p className="text-xs text-slate-500 mb-1">{data.complaint}...</p>
                            <p className="text-sm">ESI: <span className="font-semibold">{data.esi}</span></p>
                            <p className="text-sm">Confidence: <span className="font-semibold">{data.confidence}%</span></p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter
                    data={esiConfidenceScatter}
                    fill="rgb(20, 184, 166)"
                    fillOpacity={0.6}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-slate-400 text-center mt-2">
              Each point represents a patient; size indicates severity
            </p>
          </div>

          {/* Chief Complaint Treemap */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-6">
              <MessageSquare className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                Chief Complaint Keywords
              </h2>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={complaintFrequency}
                  dataKey="value"
                  aspectRatio={4 / 3}
                  stroke="#fff"
                  content={<TreemapContent x={0} y={0} width={0} height={0} name="" value={0} />}
                />
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-slate-400 text-center mt-2">
              Most frequent terms in patient chief complaints
            </p>
          </div>
        </div>

        {/* Acuity Summary Cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-xl border-2 border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-900/20 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-red-800 dark:text-red-300">Critical (ESI 1)</span>
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <p className="text-4xl font-bold text-red-700 dark:text-red-400">
              {stats.byESI[1]}
            </p>
            <p className="text-xs text-red-600/70 dark:text-red-400/70 mt-1">
              Immediate resuscitation
            </p>
          </div>
          <div className="rounded-xl border-2 border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-900/20 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-amber-800 dark:text-amber-300">Urgent (ESI 2-3)</span>
              <Clock className="h-5 w-5 text-amber-600" />
            </div>
            <p className="text-4xl font-bold text-amber-700 dark:text-amber-400">
              {stats.byESI[2] + stats.byESI[3]}
            </p>
            <p className="text-xs text-amber-600/70 dark:text-amber-400/70 mt-1">
              Time-sensitive care
            </p>
          </div>
          <div className="rounded-xl border-2 border-emerald-200 dark:border-emerald-900/50 bg-emerald-50 dark:bg-emerald-900/20 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-emerald-800 dark:text-emerald-300">Minor (ESI 4-5)</span>
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            </div>
            <p className="text-4xl font-bold text-emerald-700 dark:text-emerald-400">
              {stats.byESI[4] + stats.byESI[5]}
            </p>
            <p className="text-xs text-emerald-600/70 dark:text-emerald-400/70 mt-1">
              Standard queue
            </p>
          </div>
        </div>

        {/* Recent Activity - Compact */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-slate-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                Recent Triage Decisions
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
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="text-left py-2 px-2 font-medium text-slate-500">Patient</th>
                  <th className="text-left py-2 px-2 font-medium text-slate-500">Chief Complaint</th>
                  <th className="text-center py-2 px-2 font-medium text-slate-500">ESI</th>
                  <th className="text-center py-2 px-2 font-medium text-slate-500">Confidence</th>
                  <th className="text-left py-2 px-2 font-medium text-slate-500">Department</th>
                </tr>
              </thead>
              <tbody>
                {mockPatients.slice(0, 5).map((patient) => (
                  <tr
                    key={patient.id}
                    className="border-b border-slate-100 dark:border-slate-800"
                  >
                    <td className="py-2 px-2">
                      <span className="font-medium text-slate-900 dark:text-slate-100">{patient.name}</span>
                      <span className="text-slate-400 ml-1 text-xs">{patient.age}{patient.gender}</span>
                    </td>
                    <td className="py-2 px-2 text-slate-600 dark:text-slate-400 max-w-48 truncate">
                      {patient.chiefComplaint}
                    </td>
                    <td className="py-2 px-2 text-center">
                      <span
                        className={cn(
                          "inline-flex h-6 w-6 items-center justify-center rounded text-white font-bold text-xs",
                          patient.aiDecision.esi === 1 ? "bg-red-600" :
                          patient.aiDecision.esi === 2 ? "bg-orange-500" :
                          patient.aiDecision.esi === 3 ? "bg-amber-500" :
                          patient.aiDecision.esi === 4 ? "bg-lime-500" : "bg-green-500"
                        )}
                      >
                        {patient.aiDecision.esi}
                      </span>
                    </td>
                    <td className="py-2 px-2 text-center">
                      <span className={cn(
                        "font-semibold tabular-nums",
                        patient.aiDecision.confidence >= 85 ? "text-emerald-600" :
                        patient.aiDecision.confidence >= 70 ? "text-amber-600" : "text-red-600"
                      )}>
                        {patient.aiDecision.confidence}%
                      </span>
                    </td>
                    <td className="py-2 px-2 text-slate-600 dark:text-slate-400">
                      {patient.aiDecision.specialists[0] || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
