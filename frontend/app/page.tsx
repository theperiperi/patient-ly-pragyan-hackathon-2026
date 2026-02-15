import Link from "next/link";
import { ArrowRight, Activity, Shield, Brain } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-950">
      <div className="container max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium mb-6">
            <Activity className="w-4 h-4" />
            AI-Native Triage System
          </div>
          <h1 className="text-5xl font-bold tracking-tight mb-4">
            Patient.ly
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            ABDM-powered AI triage system for emergency departments. AI makes decisions, humans approve.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 shadow-lg border">
            <div className="w-12 h-12 rounded-xl bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center mb-4">
              <Brain className="w-6 h-6 text-violet-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">AI-First Decisions</h3>
            <p className="text-muted-foreground text-sm">
              AI analyzes patient data and makes complete triage recommendations. ESI level, bay assignment, specialist calls, tests - all decided upfront.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 shadow-lg border">
            <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Human Oversight</h3>
            <p className="text-muted-foreground text-sm">
              Nurses review AI decisions with full reasoning transparency. Slide to approve, modify, or override - with confidence scores to guide priorities.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 shadow-lg border">
            <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">ABDM Integration</h3>
            <p className="text-muted-foreground text-sm">
              Pulls complete patient history from ABDM network - conditions, medications, allergies, recent encounters - all in one view.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            href="/queue"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-primary text-primary-foreground font-semibold text-lg hover:opacity-90 transition-opacity"
          >
            Open Triage Queue
            <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="mt-4 text-sm text-muted-foreground">
            3 patients waiting for review • 94.2% AI accuracy today
          </p>
        </div>
      </div>
    </div>
  );
}
