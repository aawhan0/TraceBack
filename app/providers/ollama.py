import json
from urllib import request

from app.agent.contracts import LLMProvider


class OllamaProvider:
    """Minimal HTTP adapter keeping Ollama outside core application logic."""

    name = "ollama"

    def __init__(self, model: str, base_url: str, timeout: float = 60.0) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
        }).encode()
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = json.load(response)
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        output = body.get("response")
        if not isinstance(output, str) or not output.strip():
            raise RuntimeError("Ollama returned no usable response")
        return output
