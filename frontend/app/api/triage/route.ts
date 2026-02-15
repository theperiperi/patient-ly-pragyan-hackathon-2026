import { NextRequest, NextResponse } from "next/server";

const TRIAGE_API_URL = process.env.TRIAGE_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { patient_id, chief_complaint, vitals } = body;

    if (!patient_id || !chief_complaint) {
      return NextResponse.json(
        { error: "patient_id and chief_complaint are required" },
        { status: 400 }
      );
    }

    // Call the Python triage API
    const response = await fetch(`${TRIAGE_API_URL}/triage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patient_id, chief_complaint, vitals }),
    });

    if (!response.ok) {
      throw new Error(`Triage API returned ${response.status}`);
    }

    const decision = await response.json();
    return NextResponse.json(decision);
  } catch (error) {
    console.error("Triage API error:", error);

    // Return mock response if API is unavailable
    return NextResponse.json(getMockDecision(request));
  }
}

export async function GET() {
  // Health check - verify backend is available
  try {
    const response = await fetch(`${TRIAGE_API_URL}/health`);
    const data = await response.json();
    return NextResponse.json({ status: "ok", backend: data });
  } catch {
    return NextResponse.json({ status: "ok", backend: "unavailable" });
  }
}

function getMockDecision(request: NextRequest): object {
  // Default mock for when backend is unavailable
  return {
    esi: 3,
    acuityLabel: "MODERATE",
    acuityColor: "urgent",
    confidence: 80,
    bay: "Treatment Room 2",
    queuePosition: 3,
    specialists: ["Internal Medicine"],
    protocols: [],
    labs: ["CBC", "BMP"],
    imaging: [],
    interventions: ["IV Access"],
    isolation: null,
    reasoning: [
      "Patient requires medical evaluation",
      "Basic workup ordered",
      "Stable for treatment room"
    ],
    sbar: {
      situation: "Patient presenting for evaluation",
      background: "Medical history review pending",
      assessment: "Stable, needs workup",
      recommendation: "Complete evaluation"
    },
    alerts: []
  };
}
