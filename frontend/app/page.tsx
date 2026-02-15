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
        {/* Step number badge */}
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 text-white font-semibold text-sm shadow-lg shadow-teal-500/25">
            {number}
          </div>
          <div className="hidden md:block h-px w-12 bg-gradient-to-r from-teal-500/50 to-transparent"></div>
        </div>

        {/* Icon container */}
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <Icon className="h-7 w-7 text-slate-700 dark:text-slate-300" />
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

          {/* Hero visual - Abstract representation */}
          <div
            className={`animate-fade-in-up mt-16 md:mt-24 relative ${mounted ? "" : "opacity-0"}`}
            style={{ animationDelay: "500ms" }}
          >
            <div className="relative mx-auto max-w-4xl">
              {/* Main card mockup */}
              <div className="relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl shadow-slate-900/10 dark:shadow-black/30 overflow-hidden">
                {/* Header bar */}
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-100 dark:bg-teal-900/50">
                      <Activity className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                    </div>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">
                      Triage Queue
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <LiveIndicator />
                    <span className="text-sm text-slate-500">Live</span>
                  </div>
                </div>

                {/* Content preview */}
                <div className="p-6 space-y-4">
                  {/* Patient card 1 */}
                  <div className="flex items-center gap-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/50 p-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-500 text-white font-bold text-sm">
                      ESI-2
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-slate-900 dark:text-slate-100">
                          Ganesh Bhat
                        </span>
                        <span className="text-sm text-slate-500">57M</span>
                        <span className="ml-auto flex items-center gap-1 text-sm font-medium text-emerald-600">
                          <Brain className="h-3.5 w-3.5" />
                          92%
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        Chest pain radiating to left arm
                      </p>
                    </div>
                  </div>

                  {/* Patient card 2 */}
                  <div className="flex items-center gap-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-900/50 p-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-amber-500 text-white font-bold text-sm">
                      ESI-3
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-slate-900 dark:text-slate-100">
                          Priya Sharma
                        </span>
                        <span className="text-sm text-slate-500">34F</span>
                        <span className="ml-auto flex items-center gap-1 text-sm font-medium text-emerald-600">
                          <Brain className="h-3.5 w-3.5" />
                          88%
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        Severe abdominal pain, nausea
                      </p>
                    </div>
                  </div>

                  {/* AI Processing indicator */}
                  <div className="flex items-center gap-4 rounded-xl bg-violet-50 dark:bg-violet-900/20 border border-violet-100 dark:border-violet-900/50 p-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-violet-500 text-white">
                      <Brain className="h-5 w-5 animate-pulse" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-violet-700 dark:text-violet-300">
                          AI Triaging...
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-violet-100 dark:bg-violet-900/50 rounded-full overflow-hidden">
                        <div className="h-full w-2/3 bg-violet-500 rounded-full animate-pulse"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating elements */}
              <div className="absolute -top-4 -right-4 md:-top-8 md:-right-8 animate-float">
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Approved</div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        24 today
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="absolute -bottom-4 -left-4 md:-bottom-8 md:-left-8 animate-float" style={{ animationDelay: "1s" }}>
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-teal-100 dark:bg-teal-900/50 flex items-center justify-center">
                      <Database className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">ABDM Linked</div>
                      <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        111 patients
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
            {/* Connection lines (desktop) */}
            <div className="hidden md:block absolute top-14 left-1/4 right-1/4 h-px bg-gradient-to-r from-teal-500/50 via-teal-500/50 to-teal-500/50"></div>

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
              description="Claude analyzes patient data and generates complete triage recommendations including ESI level, bay assignment, and required interventions."
              highlight="Powered by Claude"
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
              <span>Powered by</span>
              <span className="font-medium text-slate-900 dark:text-slate-100">Claude</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
