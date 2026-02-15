"""
Triage Agent API - Fast AI triaging with structured JSON output.

Uses Claude Haiku for speed, returns JSON matching frontend schema.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Any

# Try to import Claude Agent SDK
try:
    from claude_agent_sdk import (
        ClaudeSDKClient,
        ClaudeAgentOptions,
        AssistantMessage,
        TextBlock,
        ToolUseBlock,
        ResultMessage,
    )
    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    print("Warning: claude_agent_sdk not installed. Using mock mode.")

PROJECT_ROOT = Path(__file__).parent


# ============================================================================
# JSON Schema for Triage Decision (matching frontend types.ts)
# ============================================================================

TRIAGE_DECISION_SCHEMA = {
    "type": "object",
    "required": ["esi", "acuityLabel", "acuityColor", "confidence", "bay", "queuePosition", "reasoning", "sbar"],
    "properties": {
        "esi": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "ESI level 1-5"
        },
        "acuityLabel": {
            "type": "string",
            "enum": ["RESUSCITATION", "EMERGENT", "MODERATE", "LESS URGENT", "NON-URGENT"],
            "description": "Acuity label for display"
        },
        "acuityColor": {
            "type": "string",
            "enum": ["critical", "urgent", "minor"],
            "description": "Acuity color for UI styling"
        },
        "confidence": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "AI confidence percentage"
        },
        "bay": {
            "type": "string",
            "description": "Recommended bay/room assignment"
        },
        "queuePosition": {
            "type": "integer",
            "minimum": 1,
            "description": "Queue position based on acuity"
        },
        "specialists": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specialists to page"
        },
        "protocols": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Clinical protocols to activate"
        },
        "labs": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lab tests to order"
        },
        "imaging": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Imaging studies to order"
        },
        "interventions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Immediate interventions"
        },
        "isolation": {
            "type": ["string", "null"],
            "description": "Isolation requirements if any"
        },
        "reasoning": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 5,
            "description": "Clinical reasoning points (1-5 items)"
        },
        "sbar": {
            "type": "object",
            "required": ["situation", "background", "assessment", "recommendation"],
            "properties": {
                "situation": {"type": "string", "description": "Brief description of patient's current situation"},
                "background": {"type": "string", "description": "Relevant medical history and context"},
                "assessment": {"type": "string", "description": "Clinical assessment and concerns"},
                "recommendation": {"type": "string", "description": "Recommended actions and next steps"}
            }
        },
        "alerts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "text"],
                "properties": {
                    "type": {"type": "string", "enum": ["critical", "warning", "info"]},
                    "text": {"type": "string"}
                }
            },
            "description": "Clinical alerts"
        }
    }
}


# ============================================================================
# System Prompt for Triage
# ============================================================================

TRIAGE_SYSTEM_PROMPT = """You are an expert Emergency Department triage nurse with access to patient medical records through ABDM (Ayushman Bharat Digital Mission).

## Your Task
Given a patient's chief complaint and their medical history from ABDM, provide a complete triage decision.

## ESI Levels
- ESI-1 (RESUSCITATION): Immediate life-saving intervention, acuityColor="critical"
- ESI-2 (EMERGENT): High risk, confused/lethargic, severe pain, acuityColor="critical"
- ESI-3 (MODERATE): Stable but needs multiple resources, acuityColor="urgent"
- ESI-4 (LESS URGENT): Stable, needs one resource, acuityColor="minor"
- ESI-5 (NON-URGENT): Stable, no resources needed, acuityColor="minor"

## Bay Assignments
- Resus Bay 1/2: ESI-1 patients
- Trauma Bay: Major trauma, ESI-1/2
- Cardiac Bay: Chest pain, arrhythmias
- Neuro Bay: Stroke symptoms, altered mental status
- Treatment Room 1-4: ESI-3 patients
- Fast Track: ESI-4/5 patients

## Common Protocols
- Stroke Protocol, Chest Pain Protocol, Sepsis Protocol, Trauma Protocol
- Diabetic Emergency, Respiratory Distress, Anaphylaxis Protocol

## Available MCP Tools
- get_patient_snapshot: Full clinical summary with context hints
- get_conditions: Medical conditions with risk flags
- get_medications: Current medications
- get_allergies: Documented allergies
- lookup_drug_allergies: Check medication conflicts

## Process
1. Call get_patient_snapshot to understand the patient's clinical context
2. Consider their conditions, medications, allergies from the snapshot
3. If they have allergies and medications, check for drug interactions
4. Factor in context hints (elderly, cardiac_history, polypharmacy, etc.)
5. Determine ESI level based on chief complaint + medical history
6. Generate complete triage decision

Be concise but thorough. Focus on clinically relevant findings."""


# ============================================================================
# Triage Functions
# ============================================================================

def get_patient_data_from_mcp(patient_id: str) -> dict[str, Any]:
    """Fetch patient data directly from MCP server."""
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))
        from mcp_triage_server.data.extractor import get_extractor

        extractor = get_extractor()
        snapshot = extractor.get_patient_snapshot(patient_id)
        if snapshot:
            # Convert Pydantic model to dict
            return snapshot.model_dump() if hasattr(snapshot, 'model_dump') else snapshot
        return None
    except Exception as e:
        print(f"MCP data fetch error: {e}")
        import traceback
        traceback.print_exc()
        return None


def build_full_response(
    patient_id: str,
    chief_complaint: str,
    vitals: Optional[dict],
    patient_data: Optional[dict],
    ai_decision: dict
) -> dict[str, Any]:
    """Build full patient response combining MCP data with AI decision."""

    # Default vitals if not provided
    default_vitals = {
        "bp": {"value": "120/80", "unit": "mmHg", "status": "normal", "trend": "stable"},
        "hr": {"value": 80, "unit": "bpm", "status": "normal", "trend": "stable"},
        "spo2": {"value": 98, "unit": "%", "status": "normal", "trend": "stable"},
        "temp": {"value": 98.6, "unit": "°F", "status": "normal", "trend": "stable"},
        "rr": {"value": 16, "unit": "/min", "status": "normal", "trend": "stable"},
        "pain": {"value": "5/10", "unit": "", "status": "warning", "trend": "stable"},
    }

    # Extract patient info from MCP data (PatientSnapshot has flat structure)
    if patient_data:
        # PatientSnapshot fields are at top level, not nested
        name = patient_data.get("name", "Unknown")
        age = patient_data.get("age", 0)
        gender = patient_data.get("gender", "M")
        abha = patient_data.get("abha_address") or patient_data.get("abha_number") or patient_id

        # Extract ABDM data - note field names from PatientSnapshot model
        conditions = patient_data.get("conditions", [])
        medications = patient_data.get("medications", [])
        allergies = patient_data.get("allergies", [])
        encounters = patient_data.get("recent_encounters", [])  # Note: recent_encounters

        # Format conditions for frontend (Condition model uses 'display' not 'name')
        abdm_conditions = [
            {
                "name": c.get("display", "Unknown"),
                "status": c.get("clinical_status", "active"),
                "source": "ABDM"
            }
            for c in conditions[:10]  # Limit to 10
        ]

        # Format medications for frontend (Medication model uses 'display' not 'name')
        # Filter out entries with empty display names
        abdm_medications = [
            {
                "name": m.get("display", ""),
                "dosage": m.get("dosage", "") or "",
                "frequency": ""  # Not in Medication model
            }
            for m in medications[:10]
            if m.get("display")  # Only include medications with a name
        ]

        # Format allergies for frontend (Allergy model uses 'display' not 'substance')
        abdm_allergies = [a.get("display", "Unknown") for a in allergies]

        # Format encounters for frontend
        abdm_encounters = [
            {
                "date": str(e.get("start_date", "")) if e.get("start_date") else "",
                "type": e.get("encounter_type", ""),
                "facility": "ABDM Record",
                "summary": e.get("reason", "") or ""
            }
            for e in encounters[:5]
        ]
    else:
        # Fallback if no patient data
        name = "Unknown Patient"
        age = 0
        gender = "M"
        abha = patient_id
        abdm_conditions = []
        abdm_medications = []
        abdm_allergies = []
        abdm_encounters = []

    # Build full response matching frontend Patient interface
    return {
        "id": patient_id,
        "name": name,
        "age": age,
        "gender": gender,
        "abha": abha,
        "arrivalTime": "Just now",
        "arrivalMode": "Walk-in",
        "chiefComplaint": chief_complaint,
        "vitals": vitals if vitals else default_vitals,
        "alerts": ai_decision.get("alerts", []),
        "abdmData": {
            "conditions": abdm_conditions,
            "medications": abdm_medications,
            "allergies": abdm_allergies,
            "encounters": abdm_encounters,
        },
        "aiDecision": {
            "esi": ai_decision.get("esi", 3),
            "acuityLabel": ai_decision.get("acuityLabel", "MODERATE"),
            "acuityColor": ai_decision.get("acuityColor", "urgent"),
            "confidence": ai_decision.get("confidence", 75),
            "bay": ai_decision.get("bay", "Treatment Room 2"),
            "queuePosition": ai_decision.get("queuePosition", 3),
            "specialists": ai_decision.get("specialists", []),
            "protocols": ai_decision.get("protocols", []),
            "labs": ai_decision.get("labs", []),
            "imaging": ai_decision.get("imaging", []),
            "interventions": ai_decision.get("interventions", []),
            "isolation": ai_decision.get("isolation"),
            "reasoning": ai_decision.get("reasoning", []),
            "sbar": ai_decision.get("sbar", {
                "situation": chief_complaint,
                "background": "",
                "assessment": "",
                "recommendation": ""
            }),
        }
    }


async def triage_patient(
    patient_id: str,
    chief_complaint: str,
    vitals: Optional[dict] = None
) -> dict[str, Any]:
    """
    Triage a patient using Claude Agent with MCP tools.

    Args:
        patient_id: ABDM patient ID (e.g., "ganesh.bhat6117@abdm")
        chief_complaint: Patient's presenting complaint
        vitals: Optional current vitals dict

    Returns:
        Dict with full patient data + AI decision matching frontend schema
    """

    # First, fetch patient data from MCP
    patient_data = get_patient_data_from_mcp(patient_id)

    if not HAS_SDK:
        return build_full_response(patient_id, chief_complaint, vitals, patient_data, get_mock_decision(chief_complaint))

    # Build vitals string if provided
    vitals_str = ""
    if vitals:
        vitals_str = f"""
Current Vitals:
- BP: {vitals.get('bp', 'N/A')}
- HR: {vitals.get('hr', 'N/A')} bpm
- SpO2: {vitals.get('spo2', 'N/A')}%
- Temp: {vitals.get('temp', 'N/A')}°F
- RR: {vitals.get('rr', 'N/A')}/min
- Pain: {vitals.get('pain', 'N/A')}/10
"""

    prompt = f"""Triage this patient:

Patient ID: {patient_id}
Chief Complaint: {chief_complaint}
{vitals_str}

Use the MCP tools to fetch their medical history, then provide your triage decision."""

    options = ClaudeAgentOptions(
        model="haiku",  # Fast model
        system_prompt=TRIAGE_SYSTEM_PROMPT,
        mcp_servers={
            "patient-triage": {
                "command": "python",
                "args": ["-m", "mcp_triage_server.server"],
                "cwd": str(PROJECT_ROOT),
            }
        },
        allowed_tools=[
            "mcp__patient-triage__get_patient_snapshot",
            "mcp__patient-triage__get_conditions",
            "mcp__patient-triage__get_medications",
            "mcp__patient-triage__get_allergies",
            "mcp__patient-triage__lookup_drug_allergies",
        ],
        permission_mode="acceptEdits",
        cwd=str(PROJECT_ROOT),
        output_format={
            "type": "json_schema",
            "schema": TRIAGE_DECISION_SCHEMA
        }
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)

            structured_output = None
            response_text = ""

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text
                if isinstance(message, ResultMessage):
                    structured_output = message.structured_output
                    break

            # Use structured output if available, otherwise parse from text
            result = structured_output
            if not result and response_text:
                # Try to parse JSON from response text
                import json
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])

            if result:
                # Build full response with patient data + AI decision
                ai_decision = {
                    "esi": result.get("esi", 3),
                    "acuityLabel": result.get("acuityLabel", "MODERATE"),
                    "acuityColor": result.get("acuityColor", "urgent"),
                    "confidence": result.get("confidence", 75),
                    "bay": result.get("bay", "Treatment Room 2"),
                    "queuePosition": result.get("queuePosition", 3),
                    "specialists": result.get("specialists", []),
                    "protocols": result.get("protocols", []),
                    "labs": result.get("labs", []),
                    "imaging": result.get("imaging", []),
                    "interventions": result.get("interventions", []),
                    "isolation": result.get("isolation"),
                    "reasoning": result.get("reasoning", ["AI assessment completed"]),
                    "sbar": result.get("sbar", {
                        "situation": chief_complaint,
                        "background": "See medical history",
                        "assessment": "Evaluation needed",
                        "recommendation": "Complete workup"
                    }),
                    "alerts": result.get("alerts", [])
                }
                return build_full_response(patient_id, chief_complaint, vitals, patient_data, ai_decision)

    except Exception as e:
        print(f"Agent error: {e}")

    # Fallback to mock
    return build_full_response(patient_id, chief_complaint, vitals, patient_data, get_mock_decision(chief_complaint))


def get_mock_decision(chief_complaint: str) -> dict[str, Any]:
    """Generate a mock decision for testing without the agent."""

    complaint_lower = chief_complaint.lower()

    if any(kw in complaint_lower for kw in ["chest pain", "heart", "cardiac"]):
        return {
            "esi": 2,
            "acuityLabel": "EMERGENT",
            "acuityColor": "critical",
            "confidence": 88,
            "bay": "Cardiac Bay",
            "queuePosition": 1,
            "specialists": ["Cardiology"],
            "protocols": ["Chest Pain Protocol"],
            "labs": ["Troponin", "BNP", "CBC", "BMP"],
            "imaging": ["ECG", "Chest X-Ray"],
            "interventions": ["IV Access", "Cardiac monitoring", "Aspirin 325mg"],
            "isolation": None,
            "reasoning": [
                "Chest pain requires urgent cardiac workup",
                "ECG and troponin needed to rule out ACS",
                "Continuous cardiac monitoring indicated"
            ],
            "sbar": {
                "situation": f"Patient presenting with {chief_complaint}",
                "background": "Cardiac workup initiated",
                "assessment": "Possible acute coronary syndrome",
                "recommendation": "Serial troponins, cardiology consult if positive"
            },
            "alerts": [{"type": "warning", "text": "Chest pain - cardiac workup required"}]
        }

    elif any(kw in complaint_lower for kw in ["breathing", "breath", "respiratory", "dyspnea"]):
        return {
            "esi": 3,
            "acuityLabel": "MODERATE",
            "acuityColor": "urgent",
            "confidence": 82,
            "bay": "Treatment Room 2",
            "queuePosition": 3,
            "specialists": ["Pulmonology"],
            "protocols": ["Respiratory Distress"],
            "labs": ["ABG", "CBC", "BMP"],
            "imaging": ["Chest X-Ray"],
            "interventions": ["Oxygen PRN", "IV Access", "Pulse oximetry"],
            "isolation": None,
            "reasoning": [
                "Respiratory symptoms require evaluation",
                "Chest X-ray to assess lung fields",
                "Oxygen therapy if SpO2 drops"
            ],
            "sbar": {
                "situation": f"Patient presenting with {chief_complaint}",
                "background": "Respiratory workup needed",
                "assessment": "Dyspnea of unclear etiology",
                "recommendation": "CXR, consider ABG if hypoxic"
            },
            "alerts": []
        }

    elif any(kw in complaint_lower for kw in ["headache", "head"]):
        return {
            "esi": 3,
            "acuityLabel": "MODERATE",
            "acuityColor": "urgent",
            "confidence": 78,
            "bay": "Treatment Room 3",
            "queuePosition": 4,
            "specialists": ["Neurology"],
            "protocols": [],
            "labs": ["CBC", "BMP"],
            "imaging": ["CT Head"],
            "interventions": ["IV Access", "Neuro checks"],
            "isolation": None,
            "reasoning": [
                "Headache requires neurological evaluation",
                "CT Head to rule out structural causes",
                "Monitor for red flag symptoms"
            ],
            "sbar": {
                "situation": f"Patient presenting with {chief_complaint}",
                "background": "Neurological workup needed",
                "assessment": "Headache of unclear etiology",
                "recommendation": "CT Head, neuro consult if abnormal"
            },
            "alerts": []
        }

    # Default ESI-3
    return {
        "esi": 3,
        "acuityLabel": "MODERATE",
        "acuityColor": "urgent",
        "confidence": 75,
        "bay": "Treatment Room 3",
        "queuePosition": 4,
        "specialists": [],
        "protocols": [],
        "labs": ["CBC", "BMP"],
        "imaging": [],
        "interventions": ["IV Access"],
        "isolation": None,
        "reasoning": [
            "Patient requires medical evaluation",
            "Basic labs ordered for workup",
            "Stable for treatment room placement"
        ],
        "sbar": {
            "situation": f"Patient presenting with {chief_complaint}",
            "background": "Awaiting full evaluation",
            "assessment": "Stable, needs workup",
            "recommendation": "Complete evaluation and reassess"
        },
        "alerts": []
    }


# ============================================================================
# FastAPI Server
# ============================================================================

def create_app():
    """Create FastAPI app for triage API."""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(
        title="Patient.ly Triage API",
        version="1.0.0",
        description="AI-powered patient triage using ABDM data"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all for dev
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class TriageRequest(BaseModel):
        patient_id: str
        chief_complaint: str
        vitals: Optional[dict] = None

    class VitalSign(BaseModel):
        value: str | int | float
        unit: str
        status: str
        trend: str = "stable"

    class Vitals(BaseModel):
        bp: VitalSign
        hr: VitalSign
        spo2: VitalSign
        temp: VitalSign
        rr: VitalSign
        pain: VitalSign

    class Condition(BaseModel):
        name: str
        status: str
        source: str

    class Medication(BaseModel):
        name: str
        dosage: str
        frequency: str

    class Encounter(BaseModel):
        date: str
        type: str
        facility: str
        summary: str

    class ABDMData(BaseModel):
        conditions: list[Condition] = []
        medications: list[Medication] = []
        allergies: list[str] = []
        encounters: list[Encounter] = []

    class SBARHandoff(BaseModel):
        situation: str
        background: str
        assessment: str
        recommendation: str

    class AIDecisionResponse(BaseModel):
        esi: int
        acuityLabel: str
        acuityColor: str
        confidence: int
        bay: str
        queuePosition: int
        specialists: list[str] = []
        protocols: list[str] = []
        labs: list[str] = []
        imaging: list[str] = []
        interventions: list[str] = []
        isolation: Optional[str] = None
        reasoning: list[str] = []
        sbar: SBARHandoff

    class Alert(BaseModel):
        type: str
        text: str

    class TriageResponse(BaseModel):
        id: str
        name: str
        age: int
        gender: str
        abha: str
        arrivalTime: str
        arrivalMode: str
        chiefComplaint: str
        vitals: Vitals
        alerts: list[Alert] = []
        abdmData: ABDMData
        aiDecision: AIDecisionResponse

    @app.get("/health")
    async def health():
        return {"status": "ok", "sdk_available": HAS_SDK}

    @app.post("/triage", response_model=TriageResponse)
    async def triage(request: TriageRequest):
        """Triage a patient and return AI decision."""
        try:
            decision = await triage_patient(
                patient_id=request.patient_id,
                chief_complaint=request.chief_complaint,
                vitals=request.vitals
            )
            return decision
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # Run as API server
        import uvicorn
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif len(sys.argv) >= 3:
        # CLI mode
        patient_id = sys.argv[1]
        chief_complaint = sys.argv[2]

        async def main():
            print(f"Triaging: {patient_id}")
            print(f"Complaint: {chief_complaint}")
            print("-" * 50)
            decision = await triage_patient(patient_id, chief_complaint)
            print(json.dumps(decision, indent=2))

        asyncio.run(main())
    else:
        print("Usage:")
        print("  python triage_agent_api.py serve              # Run API server")
        print("  python triage_agent_api.py <patient_id> <complaint>  # CLI triage")
        print()
        print("Example:")
        print("  python triage_agent_api.py serve")
        print("  python triage_agent_api.py 'ganesh.bhat6117@abdm' 'chest pain'")
