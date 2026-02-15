"""
Triage Agent - AI-powered patient triaging using Claude Agent SDK.

This agent uses the patient-triage MCP server to access patient data
and make triage decisions (ESI levels, disposition, recommendations).
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    ResultMessage,
)

# Project root where MCP server is located
PROJECT_ROOT = Path(__file__).parent

# System prompt for the triage agent
TRIAGE_SYSTEM_PROMPT = """You are an expert Emergency Department triage nurse with access to patient medical records through ABDM (Ayushman Bharat Digital Mission).

Your role is to:
1. Assess patients and determine appropriate ESI (Emergency Severity Index) levels
2. Identify clinical red flags and high-risk conditions
3. Recommend appropriate disposition (resuscitation bay, trauma bay, fast track, etc.)
4. Flag drug allergies and medication interactions
5. Generate structured triage assessments

## ESI Levels (Emergency Severity Index)
- **ESI-1 (Resuscitation)**: Immediate life-saving intervention required
- **ESI-2 (Emergent)**: High risk, confused/lethargic, severe pain/distress
- **ESI-3 (Urgent)**: Stable but needs multiple resources, moderate pain
- **ESI-4 (Less Urgent)**: Stable, needs one resource
- **ESI-5 (Non-Urgent)**: Stable, no resources needed

## Available Tools
You have access to patient data through these MCP tools:
- `search_patients` - Find patients by name, ABHA number
- `list_patients` - List all patients
- `get_patient_snapshot` - Full clinical summary with context hints
- `get_conditions` - Medical conditions with risk flags
- `get_medications` - Current medications
- `get_allergies` - Documented allergies
- `get_vitals` - Recent vital signs
- `get_encounters` - Healthcare visit history
- `lookup_drug_allergies` - Check medication conflicts

## Context Hints
The `get_patient_snapshot` tool provides clinical hints:
- `elderly`: Age >= 65
- `pediatric`: Age < 18
- `cardiac_history`: Cardiac conditions present
- `respiratory_history`: Respiratory conditions present
- `diabetic`: Diabetes present
- `polypharmacy`: 5+ active medications
- `recent_ed_visit`: ED visit in last 30 days
- `immunocompromised`: Immunocompromising conditions
- `high_risk_conditions`: List of flagged conditions

Use these hints along with clinical data to make informed triage decisions.

## Output Format
When triaging a patient, provide:
1. **Patient Summary**: Demographics and chief complaint
2. **Clinical Assessment**: Key findings from history/vitals
3. **Risk Factors**: Based on context hints and conditions
4. **ESI Level**: Your recommended level with reasoning
5. **Disposition**: Recommended treatment area
6. **Alerts**: Any critical warnings (allergies, drug interactions, etc.)
"""


async def run_triage_session():
    """Run an interactive triage session."""

    # Configure the agent with MCP server
    options = ClaudeAgentOptions(
        # Use Claude Code's system prompt as base, append triage instructions
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": TRIAGE_SYSTEM_PROMPT,
        },
        # MCP server configuration - connects to our patient-triage server
        mcp_servers={
            "patient-triage": {
                "command": "python",
                "args": ["-m", "mcp_triage_server.server"],
                "cwd": str(PROJECT_ROOT),
            }
        },
        # Allow all patient-triage MCP tools
        allowed_tools=[
            "mcp__patient-triage__search_patients",
            "mcp__patient-triage__list_patients",
            "mcp__patient-triage__get_patient_snapshot",
            "mcp__patient-triage__get_conditions",
            "mcp__patient-triage__get_medications",
            "mcp__patient-triage__get_allergies",
            "mcp__patient-triage__get_vitals",
            "mcp__patient-triage__get_encounters",
            "mcp__patient-triage__lookup_drug_allergies",
        ],
        # Auto-accept tool usage
        permission_mode="acceptEdits",
        # Working directory
        cwd=str(PROJECT_ROOT),
    )

    print("=" * 60)
    print("PATIENT TRIAGE AGENT")
    print("=" * 60)
    print("AI-powered triage using ABDM patient data")
    print("Type 'exit' to quit, 'list' to see patients")
    print("=" * 60)

    async with ClaudeSDKClient(options=options) as client:
        while True:
            # Get user input
            print()
            user_input = input("Triage> ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Ending triage session.")
                break

            # Send query to agent
            await client.query(user_input)

            # Process response
            print()
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text)
                        elif isinstance(block, ToolUseBlock):
                            print(f"[Using tool: {block.name}]")
                        elif isinstance(block, ToolResultBlock):
                            pass  # Tool results are processed internally

                elif isinstance(message, ResultMessage):
                    if message.is_error:
                        print(f"[Error: {message.result}]")


async def triage_patient(patient_id: str):
    """Perform a single triage assessment for a patient."""

    options = ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": TRIAGE_SYSTEM_PROMPT,
        },
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
            "mcp__patient-triage__get_vitals",
            "mcp__patient-triage__get_encounters",
            "mcp__patient-triage__lookup_drug_allergies",
        ],
        permission_mode="acceptEdits",
        cwd=str(PROJECT_ROOT),
    )

    prompt = f"""Perform a comprehensive triage assessment for patient: {patient_id}

1. First, get the patient snapshot to understand their clinical context
2. Review their conditions, medications, allergies, and recent vitals
3. Consider the context hints (elderly, cardiac history, polypharmacy, etc.)
4. Assign an appropriate ESI level with reasoning
5. Provide a structured triage assessment
"""

    print(f"\n{'='*60}")
    print(f"TRIAGE ASSESSMENT: {patient_id}")
    print(f"{'='*60}\n")

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock):
                        print(f"[Fetching: {block.name.replace('mcp__patient-triage__', '')}]")

            elif isinstance(message, ResultMessage):
                print(f"\n{'='*60}")
                print(f"Assessment complete. Cost: ${message.total_cost_usd or 0:.4f}")
                print(f"{'='*60}")


async def batch_triage(patient_ids: list[str]):
    """Triage multiple patients in sequence."""
    for patient_id in patient_ids:
        await triage_patient(patient_id)
        print("\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # If patient IDs provided, triage those patients
        patient_ids = sys.argv[1:]
        asyncio.run(batch_triage(patient_ids))
    else:
        # Interactive mode
        asyncio.run(run_triage_session())
