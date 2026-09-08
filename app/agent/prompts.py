from app.models.domain import Incident

SYSTEM_PROMPT = """You are Traceback, a software incident investigation agent.
Reason from the incident and evidence available through tools.
Never invent evidence IDs.
Return JSON only with exactly these fields:
incident_id, root_cause, evidence_ids, confidence, recommended_action.
confidence must be a number from 0 to 1.
"""


def build_investigation_prompt(incident: Incident) -> str:
    return (
        "Investigate this incident using the evidence tool. "
        "Select only evidence that materially supports the diagnosis.\n\n"
        f"Incident ID: {incident.id}\n"
        f"Title: {incident.title}\n"
        f"Description: {incident.description}\n"
        "First gather evidence, then produce the JSON diagnosis."
    )
