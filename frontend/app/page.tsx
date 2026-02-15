"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Activity,
  Shield,
  Brain,
  Zap,
  Users,
  CheckCircle2,
  Stethoscope,
  FileText,
  AlertTriangle,
  TrendingUp,
  Database,
  Sparkles,
  MapPin,
  FlaskConical,
  Scan,
  Syringe,
  ChevronLeft,
  Heart,
} from "lucide-react";

// Animated counter component
function AnimatedNumber({ value, suffix = "" }: { value: number; suffix?: string }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const duration = 2000;
    const steps = 60;
    const increment = value / steps;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      setCurrent(Math.min(Math.round(increment * step * 10) / 10, value));
      if (step >= steps) clearInterval(timer);
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  return (
    <span className="tabular-nums">
      {current.toLocaleString()}
      {suffix}
    </span>
  );
}

// Live pulse indicator
function LiveIndicator() {
  return (
    <span className="relative flex h-2.5 w-2.5">
      <span className="animate-pulse-ring absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
    </span>
  );
}

// Workflow step component
function WorkflowStep({
  number,
  icon: Icon,
  title,
  description,
  delay,
}: {
  number: number;
  icon: React.ElementType;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <div
      className="animate-fade-in-up relative"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="relative z-10 flex flex-col items-center text-center md:items-start md:text-left">
        {/* Icon container with number badge */}
        <div className="relative mb-4">
          {/* Number badge - top left */}
          <div className="absolute -top-2 -left-2 z-10 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 text-white font-bold text-xs shadow-lg shadow-teal-500/25">
            {number}
          </div>
          {/* Icon box */}
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <Icon className="h-7 w-7 text-slate-700 dark:text-slate-300" />
          </div>
        </div>

        {/* Content */}
        <h3 className="mb-2 text-lg font-semibold text-slate-900 dark:text-slate-100">
          {title}
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 max-w-xs">
          {description}
        </p>
      </div>
    </div>
  );
}

// Feature card component
function FeatureCard({
  icon: Icon,
  title,
  description,
  highlight,
  delay,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  highlight?: string;
  delay: number;
}) {
  return (
    <div
      className="animate-fade-in-up group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-all duration-300 hover:border-teal-500/50 hover:shadow-xl hover:shadow-teal-500/5"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

      <div className="relative z-10">
        {/* Icon */}
        <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800 group-hover:bg-teal-50 dark:group-hover:bg-teal-900/30 transition-colors duration-300">
          <Icon className="h-6 w-6 text-slate-600 dark:text-slate-400 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors duration-300" />
        </div>

        {/* Content */}
        <h3 className="mb-2 text-lg font-semibold text-slate-900 dark:text-slate-100">
          {title}
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          {description}
        </p>

        {/* Highlight badge */}
        {highlight && (
          <div className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-teal-50 dark:bg-teal-900/30 px-3 py-1 text-xs font-medium text-teal-700 dark:text-teal-300">
            <Sparkles className="h-3 w-3" />
            {highlight}
          </div>
        )}
      </div>
    </div>
  );
}

// Stat card component
function StatCard({
  value,
  suffix,
  label,
  trend,
  delay,
}: {
  value: number;
  suffix?: string;
  label: string;
  trend?: string;
  delay: number;
}) {
  return (
    <div
      className="animate-fade-in-up text-center"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-slate-100 mb-1">
        <AnimatedNumber value={value} suffix={suffix} />
      </div>
      <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">{label}</div>
      {trend && (
        <div className="inline-flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
          <TrendingUp className="h-3 w-3" />
          {trend}
        </div>
      )}
    </div>
  );
}

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Background elements */}
      <div className="fixed inset-0 bg-grid-pattern pointer-events-none"></div>
      <div className="fixed inset-0 bg-radial-fade pointer-events-none"></div>

      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-32">
        <div className="container max-w-6xl mx-auto px-4">
          {/* Top badge */}
          <div
            className={`animate-fade-in-up flex justify-center mb-8 ${mounted ? "" : "opacity-0"}`}
            style={{ animationDelay: "100ms" }}
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm px-4 py-2 text-sm">
              <LiveIndicator />
              <span className="text-slate-600 dark:text-slate-400">
                AI Triage System
              </span>
              <span className="text-slate-300 dark:text-slate-700">|</span>
              <span className="font-medium text-slate-900 dark:text-slate-100">
                3 patients in queue
              </span>
            </div>
          </div>

          {/* Main headline */}
          <div className="text-center max-w-4xl mx-auto">
            <h1
              className={`animate-fade-in-up font-display text-5xl md:text-7xl lg:text-8xl tracking-tight mb-6 ${mounted ? "" : "opacity-0"}`}
              style={{ animationDelay: "200ms" }}
            >
              <span className="text-slate-900 dark:text-slate-100">Emergency </span>
              <span className="italic text-teal-600 dark:text-teal-400">triage</span>
              <br />
              <span className="text-slate-900 dark:text-slate-100">reimagined</span>
            </h1>

            <p
              className={`animate-fade-in-up text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed ${mounted ? "" : "opacity-0"}`}
              style={{ animationDelay: "300ms" }}
            >
              AI analyzes patient records from ABDM, determines ESI levels, and generates complete triage decisions.{" "}
              <span className="text-slate-900 dark:text-slate-100 font-medium">
                Nurses review and approve in seconds.
              </span>
            </p>

            {/* CTA buttons */}
            <div
              className={`animate-fade-in-up flex flex-col sm:flex-row items-center justify-center gap-4 ${mounted ? "" : "opacity-0"}`}
              style={{ animationDelay: "400ms" }}
            >
              <Link
                href="/queue"
                className="group inline-flex items-center gap-2 rounded-full bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 px-8 py-4 font-semibold text-base transition-all duration-300 hover:gap-4 hover:shadow-xl hover:shadow-slate-900/20 dark:hover:shadow-slate-100/20"
              >
                Open Triage Queue
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-500">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>94.2% AI accuracy today</span>
              </div>
            </div>
          </div>

          {/* Hero visual - Triage Approval Page Mockup */}
          <div
            className={`animate-fade-in-up mt-16 md:mt-24 relative ${mounted ? "" : "opacity-0"}`}
            style={{ animationDelay: "500ms" }}
          >
            <div className="relative mx-auto max-w-lg">
              {/* Mobile device frame */}
              <div className="relative rounded-[2.5rem] border-[8px] border-slate-800 dark:border-slate-700 bg-slate-800 dark:bg-slate-700 shadow-2xl shadow-slate-900/30 dark:shadow-black/50 overflow-hidden">
                {/* Notch */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-slate-800 dark:bg-slate-700 rounded-b-2xl z-10"></div>

                {/* Screen content */}
                <div className="bg-white dark:bg-slate-900 rounded-[2rem] overflow-hidden">
                  {/* App header */}
                  <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100 dark:border-slate-800 pt-8">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800">
                        <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                      </div>
                      <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">Review</span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-medium text-slate-600 dark:text-slate-400">
                        1/3
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <LiveIndicator />
                      <span className="text-xs text-slate-500">2 pending</span>
                    </div>
                  </div>

                  {/* Patient info */}
                  <div className="px-5 py-4 space-y-4">
                    {/* Patient header */}
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Ganesh Bhat</h3>
                        <p className="text-sm text-slate-500">57 years • Male • MRN: 847291</p>
                      </div>
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 dark:bg-red-900/40 text-xs font-medium text-red-700 dark:text-red-300">
                        <Heart className="h-3 w-3" />
                        Cardiac
                      </span>
                    </div>

                    {/* Chief complaint */}
                    <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/40">
                      <p className="text-sm font-medium text-red-800 dark:text-red-200">
                        &ldquo;Chest pain radiating to left arm, onset 2 hours ago, associated with diaphoresis&rdquo;
                      </p>
                    </div>

                    {/* AI Decision header */}
                    <div className="flex items-center gap-3">
                      <div className="px-3 py-1.5 rounded font-semibold text-sm bg-red-600 text-white">
                        ESI-2 Urgent
                      </div>
                      <div className="flex items-baseline gap-1">
                        <span className="text-xl font-semibold text-emerald-600 dark:text-emerald-400 tabular-nums">92%</span>
                        <span className="text-xs text-slate-500">confidence</span>
                      </div>
                    </div>

                    {/* Bay + Page */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase tracking-wide mb-0.5">
                          <MapPin className="w-3 h-3" />
                          <span>Bay</span>
                        </div>
                        <div className="font-semibold text-sm text-slate-900 dark:text-slate-100">Trauma Bay 1</div>
                      </div>
                      <div className="p-2.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase tracking-wide mb-0.5">
                          <Users className="w-3 h-3" />
                          <span>Page</span>
                        </div>
                        <div className="font-semibold text-sm text-slate-900 dark:text-slate-100">Cardiology</div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                      <div className="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
                        <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">AI Suggested Actions</span>
                      </div>
                      <div className="divide-y divide-slate-100 dark:divide-slate-800">
                        {/* Protocols */}
                        <div className="flex items-start gap-2 px-2.5 py-2.5 bg-amber-50/50 dark:bg-amber-900/10">
                          <Zap className="w-3.5 h-3.5 text-amber-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-[10px] text-amber-700 dark:text-amber-400 font-medium block mb-1">Protocols</span>
                            <div className="flex flex-wrap gap-1">
                              <span className="px-2 py-0.5 rounded text-[10px] bg-amber-100 dark:bg-amber-900/30 border border-amber-300 dark:border-amber-700 text-amber-800 dark:text-amber-300 font-medium">STEMI Alert</span>
                              <span className="px-2 py-0.5 rounded text-[10px] bg-amber-100 dark:bg-amber-900/30 border border-amber-300 dark:border-amber-700 text-amber-800 dark:text-amber-300 font-medium">Chest Pain</span>
                            </div>
                          </div>
                        </div>
                        {/* Labs */}
                        <div className="flex items-start gap-2 px-2.5 py-2.5">
                          <FlaskConical className="w-3.5 h-3.5 text-teal-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-[10px] text-slate-500 font-medium block mb-1">Labs</span>
                            <div className="flex flex-wrap gap-1">
                              <span className="px-2 py-0.5 rounded text-[10px] bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800 text-teal-800 dark:text-teal-300">Troponin</span>
                              <span className="px-2 py-0.5 rounded text-[10px] bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800 text-teal-800 dark:text-teal-300">BMP</span>
                              <span className="px-2 py-0.5 rounded text-[10px] bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800 text-teal-800 dark:text-teal-300">CBC</span>
                            </div>
                          </div>
                        </div>
                        {/* Imaging */}
                        <div className="flex items-start gap-2 px-2.5 py-2.5 bg-slate-50/50 dark:bg-slate-800/50">
                          <Scan className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-[10px] text-slate-500 font-medium block mb-1">Imaging</span>
                            <div className="flex flex-wrap gap-1">
                              <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300">12-lead ECG</span>
                              <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300">Chest X-ray</span>
                            </div>
                          </div>
                        </div>
                        {/* Interventions */}
                        <div className="flex items-start gap-2 px-2.5 py-2.5">
                          <Syringe className="w-3.5 h-3.5 text-red-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-[10px] text-slate-500 font-medium block mb-1">Interventions</span>
                            <div className="flex flex-wrap gap-1">
                              <span className="px-2 py-0.5 rounded text-[10px] bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300">IV Access</span>
                              <span className="px-2 py-0.5 rounded text-[10px] bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300">Aspirin 325mg</span>
                              <span className="px-2 py-0.5 rounded text-[10px] bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300">O2 if SpO2 &lt;94%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sticky footer - Slide to approve */}
                  <div className="px-5 py-4 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900">
                    {/* Slide to approve mockup */}
                    <div className="relative h-14 rounded-lg overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                      {/* Progress fill - animated */}
                      <div className="absolute inset-y-0 left-0 w-1/2 bg-emerald-200 dark:bg-emerald-900/50 animate-pulse"></div>

                      {/* Slider knob - positioned at 50% mark */}
                      <div className="absolute top-1 bottom-1 w-12 rounded bg-emerald-600 flex items-center justify-center" style={{ left: "calc(50% - 3rem)" }}>
                        <ArrowRight className="w-5 h-5 text-white" />
                      </div>

                      {/* Text */}
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span className="font-medium text-sm text-emerald-800 dark:text-emerald-300">
                          Slide to approve →
                        </span>
                      </div>
                    </div>

                    {/* Alternative buttons */}
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      <button className="h-9 px-4 rounded border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 font-medium text-xs">
                        Modify
                      </button>
                      <button className="h-9 px-4 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-medium text-xs">
                        Manual Review
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating cards */}
              <div className="absolute -top-4 -right-4 md:top-8 md:-right-16 animate-float">
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center">
                      <Brain className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">AI Analysis</div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        Complete
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="absolute -bottom-4 -left-4 md:bottom-24 md:-left-16 animate-float" style={{ animationDelay: "1s" }}>
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-teal-100 dark:bg-teal-900/50 flex items-center justify-center">
                      <Database className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">ABDM History</div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        12 records
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-20 md:py-32 border-t border-slate-100 dark:border-slate-800">
        <div className="container max-w-6xl mx-auto px-4">
          {/* Section header */}
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-5xl text-slate-900 dark:text-slate-100 mb-4">
              Three steps to <span className="italic text-teal-600 dark:text-teal-400">better</span> triage
            </h2>
            <p className="text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
              From patient arrival to approved care plan in under 60 seconds
            </p>
          </div>

          {/* Workflow steps */}
          <div className="grid md:grid-cols-3 gap-8 md:gap-12 relative">
            <WorkflowStep
              number={1}
              icon={Stethoscope}
              title="Patient Arrives"
              description="Basic vitals and chief complaint are captured. ABDM records are instantly pulled."
              delay={600}
            />
            <WorkflowStep
              number={2}
              icon={Brain}
              title="AI Analyzes"
              description="Claude processes medical history, identifies risks, and generates a complete triage decision."
              delay={700}
            />
            <WorkflowStep
              number={3}
              icon={Shield}
              title="Nurse Approves"
              description="Review AI reasoning, adjust if needed, and approve with a single swipe. Patient is routed."
              delay={800}
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-20 md:py-32 bg-slate-50 dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-800">
        <div className="container max-w-6xl mx-auto px-4">
          {/* Section header */}
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-5xl text-slate-900 dark:text-slate-100 mb-4">
              Built for <span className="italic text-teal-600 dark:text-teal-400">real</span> emergency departments
            </h2>
            <p className="text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
              Every feature designed with input from triage nurses and emergency physicians
            </p>
          </div>

          {/* Features grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={Database}
              title="ABDM Integration"
              description="Instantly pulls complete patient history from India's health data network. Conditions, medications, allergies, and recent encounters in one view."
              highlight="Real-time sync"
              delay={900}
            />
            <FeatureCard
              icon={Brain}
              title="AI-First Decisions"
              description="AI analyzes patient data and generates complete triage recommendations including ESI level, bay assignment, and required interventions."
              delay={1000}
            />
            <FeatureCard
              icon={Shield}
              title="Human Oversight"
              description="Every AI decision includes full reasoning. Nurses review, modify if needed, and approve with confidence. Nothing happens without human sign-off."
              delay={1100}
            />
            <FeatureCard
              icon={AlertTriangle}
              title="Smart Alerts"
              description="Automatic flags for drug allergies, high-risk conditions, and critical symptoms. Never miss an important clinical detail."
              delay={1200}
            />
            <FeatureCard
              icon={FileText}
              title="SBAR Handoffs"
              description="AI generates structured Situation-Background-Assessment-Recommendation notes for seamless handoffs to treating physicians."
              delay={1300}
            />
            <FeatureCard
              icon={Zap}
              title="Sub-60s Triage"
              description="Complete AI analysis, nurse review, and approval in under a minute. Get patients to the right care faster."
              delay={1400}
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20 md:py-32 border-t border-slate-100 dark:border-slate-800">
        <div className="container max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
            <StatCard
              value={94.2}
              suffix="%"
              label="AI Accuracy"
              trend="+2.1% this week"
              delay={1500}
            />
            <StatCard
              value={47}
              suffix="s"
              label="Avg. Triage Time"
              trend="-12s from baseline"
              delay={1600}
            />
            <StatCard
              value={111}
              label="ABDM Patients"
              delay={1700}
            />
            <StatCard
              value={24}
              label="Triaged Today"
              delay={1800}
            />
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-20 md:py-32 bg-slate-900 dark:bg-slate-950 border-t border-slate-800">
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.02]"></div>
        <div className="container max-w-4xl mx-auto px-4 text-center relative z-10">
          <h2 className="font-display text-3xl md:text-5xl text-white mb-6">
            Ready to transform your <span className="italic text-teal-400">triage</span>?
          </h2>
          <p className="text-lg text-slate-400 mb-10 max-w-xl mx-auto">
            Join the future of emergency department triage. AI-powered decisions with human oversight.
          </p>
          <Link
            href="/queue"
            className="group inline-flex items-center gap-2 rounded-full bg-white text-slate-900 px-8 py-4 font-semibold text-base transition-all duration-300 hover:gap-4 hover:shadow-xl hover:shadow-white/10"
          >
            Open Triage Queue
            <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
          </Link>
          <p className="mt-6 text-sm text-slate-500">
            <Users className="inline h-4 w-4 mr-1" />
            3 patients waiting for review
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-100 dark:border-slate-800">
        <div className="container max-w-6xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-teal-600" />
              <span className="font-semibold text-slate-900 dark:text-slate-100">Patient.ly</span>
            </div>
            <div>
              AI-Native Triage System for Emergency Departments
            </div>
            <div className="flex items-center gap-1">
              <span>Built with</span>
              <span className="text-red-500">♥</span>
              <span>by</span>
              <span className="font-medium text-slate-900 dark:text-slate-100">Delta</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
