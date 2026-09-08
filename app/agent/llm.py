from app.agent.contracts import LLMProvider, ToolRequest
from app.agent.parser import parse_diagnosis
from app.agent.prompts import SYSTEM_PROMPT, build_investigation_prompt
from app.models.domain import Diagnosis, Incident, IncidentScenario
from app.tools.scenario import ScenarioEvidenceTool


class LLMInvestigator:
    """LLM-backed investigator with explicit evidence and output boundaries."""

    def __init__(self, scenario: IncidentScenario, provider: LLMProvider) -> None:
        self._scenario = scenario
        self._provider = provider
        self._tool = ScenarioEvidenceTool(scenario)

    def investigate(self, incident: Incident) -> Diagnosis:
        if incident.id != self._scenario.incident.id:
            raise ValueError("Incident does not belong to the configured scenario")

        response = self._tool.execute(
            ToolRequest(name=self._tool.name, arguments={"operation": "list"})
        )
        evidence_context = "\n".join(
            f"[{item.id}] {item.source}/{item.kind}: {item.content}"
            for item in response.evidence
        )
        user_prompt = (
            f"{build_investigation_prompt(incident)}\n\n"
            f"Available evidence:\n{evidence_context}"
        )
        diagnosis = parse_diagnosis(
            self._provider.complete(SYSTEM_PROMPT, user_prompt)
        )
        if diagnosis.incident_id != incident.id:
            raise ValueError("LLM diagnosis incident_id does not match incident")
        return diagnosis
