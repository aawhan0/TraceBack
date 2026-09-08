import json
from typing import Any

from pydantic import ValidationError

from app.models.domain import Diagnosis


class DiagnosisParseError(ValueError):
    """Raised when an LLM response cannot become a valid diagnosis."""


def parse_diagnosis(raw: str) -> Diagnosis:
    text = raw.strip()
    if not text:
        raise DiagnosisParseError("LLM returned an empty response")

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1] == "```":
            text = "\n".join(lines[1:-1]).strip()

    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DiagnosisParseError("LLM response is not valid JSON") from exc

    try:
        return Diagnosis.model_validate(payload)
    except ValidationError as exc:
        raise DiagnosisParseError("LLM response does not match Diagnosis") from exc
