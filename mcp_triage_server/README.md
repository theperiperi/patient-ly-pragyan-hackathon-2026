# MCP Triage Server

MCP (Model Context Protocol) server for patient triaging, exposing clinical data and context hints to LLM agents.

## Design Philosophy

**LLM Agent = Intelligence Layer**

This server provides data and context hints, NOT clinical decisions. The LLM agent uses this information to:
- Assess ESI (Emergency Severity Index) levels
- Make triage disposition decisions
- Generate clinical handoffs

## Tools

### Patient Discovery
- `search_patients` - Find patients by name, ABHA number, or ABHA address
- `list_patients` - List all patients with pagination

### Clinical Snapshot
- `get_patient_snapshot` - Comprehensive clinical summary with context hints

### Clinical History
- `get_conditions` - Medical conditions with risk flags
- `get_medications` - Current and past medications
- `get_allergies` - Documented allergies
- `get_vitals` - Recent vital signs
- `get_encounters` - Healthcare visit history

### Safety Checks
- `lookup_drug_allergies` - Check medication against patient allergies

## Context Hints

The `get_patient_snapshot` tool surfaces these hints:

| Hint | Description |
|------|-------------|
| `elderly` | True if patient is 65+ |
| `pediatric` | True if patient is under 18 |
| `cardiac_history` | True if cardiac conditions present |
| `respiratory_history` | True if respiratory conditions present |
| `diabetic` | True if diabetic condition present |
| `polypharmacy` | True if 5+ active medications |
| `recent_ed_visit` | True if ED visit in last 30 days |
| `high_risk_conditions` | List of flagged high-risk conditions |
| `allergy_count` | Number of documented allergies |
| `immunocompromised` | True if immunocompromising conditions |

## Installation

```bash
cd mcp_triage_server
pip install -e .
```

## Usage with Claude Code

Add to your Claude Code MCP settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "patient-triage": {
      "command": "python",
      "args": ["-m", "mcp_triage_server.server"],
      "cwd": "/Users/blitz/patient-ly-pragyan-hackathon-2026"
    }
  }
}
```

Or run directly:

```bash
cd /Users/blitz/patient-ly-pragyan-hackathon-2026
python -m mcp_triage_server.server
```

## Validation

All 9 tools validated successfully:
- 111 FHIR patient bundles loaded
- Patient search by name, ABHA, and partial match working
- Clinical snapshot with context hints working
- Drug allergy lookup with drug class matching working
- ABHA address resolution working

## Data Source

Uses ABDM-compliant FHIR bundles from:
- `abdm-local-dev-kit/data/seed/fhir_bundles/` - 111 patient bundles
- `abdm-local-dev-kit/data/seed/patients.json` - Patient index
