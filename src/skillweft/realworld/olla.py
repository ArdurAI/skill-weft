from __future__ import annotations

"""Real-world test helpers for Olla/OpenAI-compatible chat-completion APIs.

The module intentionally uses only the Python standard library so real-world
smoke tests can run after an editable install without extra dependencies.
"""

from dataclasses import dataclass
import json
from typing import Any, Mapping
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://api.olla.ai/v1"
DEFAULT_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class OllaConfig:
    api_key: str | None
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "OllaConfig":
        base_url = env.get("OLLA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        model = env.get("OLLA_MODEL", DEFAULT_MODEL)
        timeout_raw = env.get("OLLA_TIMEOUT_SECONDS", "60")
        try:
            timeout_seconds = int(timeout_raw)
        except ValueError:
            timeout_seconds = 60
        return cls(
            api_key=env.get("OLLA_API_KEY"),
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
        )

    @property
    def ready(self) -> bool:
        return bool(self.api_key)

    @property
    def missing_reason(self) -> str:
        if self.ready:
            return ""
        return "Set OLLA_API_KEY to run Olla real-world tests."

    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def safe_summary(self) -> str:
        key_status = "present" if self.api_key else "missing"
        return f"OllaConfig(base_url={self.base_url!r}, model={self.model!r}, api_key={key_status})"


def build_chat_completion_payload(
    *,
    model: str,
    system: str,
    user: str,
    temperature: float = 0,
    response_format: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "model": model,
        "temperature": temperature,
        "response_format": response_format or {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }


def extract_message_text(payload: Mapping[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("chat-completion response missing choices")
    first = choices[0]
    if not isinstance(first, Mapping):
        raise ValueError("chat-completion choice is not an object")
    message = first.get("message")
    if isinstance(message, Mapping) and isinstance(message.get("content"), str):
        return message["content"]
    if isinstance(first.get("text"), str):
        return first["text"]
    raise ValueError("chat-completion response missing message content")


def call_olla_chat(config: OllaConfig, *, system: str, user: str) -> str:
    if not config.ready:
        raise ValueError(config.missing_reason)
    payload = build_chat_completion_payload(model=config.model, system=system, user=user)
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        config.chat_completions_url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SkillWeft-real-world-tests/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", "replace")[:1000]
        raise RuntimeError(f"Olla API HTTP {exc.code}: {error_body}") from exc
    return extract_message_text(response_payload)


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        # Tolerate fenced JSON despite the strict prompt.
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].lstrip()
    parsed = json.loads(stripped)
    if not isinstance(parsed, dict):
        raise ValueError("expected JSON object")
    return parsed
