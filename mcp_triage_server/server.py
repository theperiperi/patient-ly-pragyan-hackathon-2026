"""MCP Server for Patient Triaging."""

import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    search_patients,
    list_patients,
    get_conditions,
    get_medications,
    get_allergies,
    get_vitals,
    get_encounters,
    get_patient_snapshot,
    lookup_drug_allergies,
)

# Create MCP server instance
app = Server("patient-triage")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available triage tools."""
    return [
        Tool(
            name="search_patients",
            description="Search patients by name, ABHA number, or ABHA address. Use this to find patients in the system.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (name, ABHA number, or ABHA address)",
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["M", "F"],
                        "description": "Filter by gender",
                    },
                    "min_age": {
                        "type": "integer",
                        "description": "Minimum age filter",
                    },
                    "max_age": {
                        "type": "integer",
                        "description": "Maximum age filter",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 20)",
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_patients",
            description="List all patients in the system with pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum patients to return (default: 50)",
                        "default": 50,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination (default: 0)",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="get_patient_snapshot",
            description="""Get comprehensive patient snapshot with context hints for triage decisions.

Returns demographics, conditions, medications, allergies, vitals, encounters, and clinical hints.

Context hints include:
- elderly: True if 65+
- pediatric: True if under 18
- cardiac_history: True if cardiac conditions present
- respiratory_history: True if respiratory conditions present
- diabetic: True if diabetic
- polypharmacy: True if 5+ active medications
- recent_ed_visit: True if ED visit in last 30 days
- high_risk_conditions: List of flagged conditions
- immunocompromised: True if immunocompromising conditions

Use these hints to inform ESI level and triage decisions.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="get_conditions",
            description="Get patient medical conditions (diagnoses) with risk flags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "resolved", "inactive"],
                        "description": "Filter by clinical status",
                    },
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="get_medications",
            description="Get patient medications with dosage information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "completed", "stopped"],
                        "description": "Filter by status",
                    },
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="get_allergies",
            description="Get patient allergies with criticality information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="get_vitals",
            description="Get patient vital signs (BP, heart rate, temperature, SpO2, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum vitals to return (default: 20)",
                        "default": 20,
                    },
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="get_encounters",
            description="Get patient healthcare encounters/visits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "Look back period in days (default: 365, 0 = all time)",
                        "default": 365,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum encounters to return (default: 20)",
                        "default": 20,
                    },
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="lookup_drug_allergies",
            description="Check if a medication conflicts with patient's documented allergies. Use this before prescribing or administering medications.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient ID or ABHA address",
                    },
                    "medication": {
                        "type": "string",
                        "description": "Name of medication to check",
                    },
                },
                "required": ["patient_id", "medication"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        match name:
            case "search_patients":
                result = search_patients(
                    query=arguments["query"],
                    gender=arguments.get("gender"),
                    min_age=arguments.get("min_age"),
                    max_age=arguments.get("max_age"),
                    limit=arguments.get("limit", 20),
                )
            case "list_patients":
                result = list_patients(
                    limit=arguments.get("limit", 50),
                    offset=arguments.get("offset", 0),
                )
            case "get_patient_snapshot":
                result = get_patient_snapshot(
                    patient_id=arguments["patient_id"],
                )
            case "get_conditions":
                result = get_conditions(
                    patient_id=arguments["patient_id"],
                    status=arguments.get("status"),
                )
            case "get_medications":
                result = get_medications(
                    patient_id=arguments["patient_id"],
                    status=arguments.get("status"),
                )
            case "get_allergies":
                result = get_allergies(
                    patient_id=arguments["patient_id"],
                )
            case "get_vitals":
                result = get_vitals(
                    patient_id=arguments["patient_id"],
                    limit=arguments.get("limit", 20),
                )
            case "get_encounters":
                result = get_encounters(
                    patient_id=arguments["patient_id"],
                    days_back=arguments.get("days_back", 365),
                    limit=arguments.get("limit", 20),
                )
            case "lookup_drug_allergies":
                result = lookup_drug_allergies(
                    patient_id=arguments["patient_id"],
                    medication=arguments["medication"],
                )
            case _:
                result = {"error": f"Unknown tool: {name}"}

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str),
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2),
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
