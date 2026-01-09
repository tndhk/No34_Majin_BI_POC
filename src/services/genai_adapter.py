from dataclasses import dataclass
from typing import Any


@dataclass
class GenAIResponse:
    text: str
    raw: Any


def _extract_text(response: Any) -> str:
    candidates = getattr(response, "candidates", None)
    if not candidates:
        return ""
    content = getattr(candidates[0], "content", None)
    parts = getattr(content, "parts", None) if content else None
    if not parts:
        return ""
    return "".join(getattr(part, "text", "") for part in parts)


class GenAIModelAdapter:
    def __init__(self, client: Any, model_name: str) -> None:
        self._client = client
        self._model_name = model_name

    def generate_content(self, prompt: str) -> GenAIResponse:
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if text is None:
            text = _extract_text(response)
        return GenAIResponse(text=text, raw=response)
