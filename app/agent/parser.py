import json
from dataclasses import dataclass
from typing import Any, Mapping

from pydantic import ValidationError

from app.models.domain import Diagnosis


class DiagnosisParseError(ValueError):
    """Raised when an LLM response cannot become a valid diagnosis."""


class AgentActionParseError(ValueError):
    """Raised when an LLM response is not a valid agent action."""


@dataclass(frozen=True)
class ToolCallAction:
    tool: str
    arguments: Mapping[str, str]


@dataclass(frozen=True)
class DiagnosisAction:
    diagnosis: Diagnosis


AgentAction = ToolCallAction | DiagnosisAction


def _strip_markdown_fence(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].startswith("```") and lines[-1] == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def _load_json_object(raw: str, *, error_cls: type[ValueError]) -> dict[str, Any]:
    text = _strip_markdown_fence(raw.strip())
    if not text:
        raise error_cls("LLM returned an empty response")

    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise error_cls("LLM response is not valid JSON") from exc

    if not isinstance(payload, dict):
        raise error_cls("LLM response must be a JSON object")
    return payload


def parse_diagnosis(raw: str) -> Diagnosis:
    payload = _load_json_object(raw, error_cls=DiagnosisParseError)

    try:
        return Diagnosis.model_validate(payload)
    except ValidationError as exc:
        raise DiagnosisParseError("LLM response does not match Diagnosis") from exc


def parse_agent_action(raw: str) -> AgentAction:
    """Parse a constrained tool_call or diagnosis action from model output."""
    payload = _load_json_object(raw, error_cls=AgentActionParseError)
    action_type = payload.get("type")

    if action_type == "tool_call":
        tool = payload.get("tool")
        arguments = payload.get("arguments", {})
        if not isinstance(tool, str) or not tool.strip():
            raise AgentActionParseError("tool_call requires a non-empty tool name")
        if not isinstance(arguments, dict):
            raise AgentActionParseError("tool_call arguments must be an object")
        normalized: dict[str, str] = {}
        for key, value in arguments.items():
            if not isinstance(key, str):
                raise AgentActionParseError("tool_call argument keys must be strings")
            if not isinstance(value, str):
                raise AgentActionParseError("tool_call argument values must be strings")
            normalized[key] = value
        return ToolCallAction(tool=tool.strip(), arguments=normalized)

    if action_type == "diagnosis":
        fields = {key: value for key, value in payload.items() if key != "type"}
        try:
            diagnosis = Diagnosis.model_validate(fields)
        except ValidationError as exc:
            raise AgentActionParseError("diagnosis action does not match Diagnosis") from exc
        return DiagnosisAction(diagnosis=diagnosis)

    raise AgentActionParseError("action type must be tool_call or diagnosis")
