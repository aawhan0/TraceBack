from app.agent.contracts import ToolRequest
from app.models.domain import Diagnosis, Incident, IncidentScenario
from app.tools.scenario import ScenarioEvidenceTool


class BaselineInvestigator:
    """Deterministic non-LLM reference investigator."""

    def __init__(self, scenario: IncidentScenario) -> None:
        self._scenario = scenario
        self._tool = ScenarioEvidenceTool(scenario)

    def investigate(self, incident: Incident) -> Diagnosis:
        if incident.id != self._scenario.incident.id:
            raise ValueError("Incident does not belong to the configured scenario")

        response = self._tool.execute(
            ToolRequest(name=self._tool.name, arguments={"operation": "list"})
        )
        matched_keywords = [
            keyword
            for keyword in self._scenario.root_cause_keywords
            if any(keyword.casefold() in item.content.casefold() for item in response.evidence)
        ]

        confidence = min(0.5 + 0.15 * len(matched_keywords), 0.95)
        return Diagnosis(
            incident_id=incident.id,
            root_cause=self._scenario.expected_root_cause,
            evidence_ids=[item.id for item in response.evidence],
            confidence=confidence,
            recommended_action=(
                "Investigate and remediate the conditions causing "
                f"{self._scenario.expected_root_cause.casefold()}."
            ),
        )
