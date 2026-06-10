from __future__ import annotations

from .base import BaseAdapter
from .claude import ClaudeAdapter
from .codex import CodexAdapter
from .cursor import CursorAdapter
from .gemini import GeminiAdapter
from .hermes import HermesAdapter

_ADAPTERS: dict[str, BaseAdapter] = {
    "claude": ClaudeAdapter(),
    "claude-code": ClaudeAdapter(),
    "codex": CodexAdapter(),
    "gemini": GeminiAdapter(),
    "hermes": HermesAdapter(),
    "cursor": CursorAdapter(),
}


def get_adapter(name: str) -> BaseAdapter:
    key = name.lower()
    if key not in _ADAPTERS:
        available = ", ".join(sorted({adapter.name for adapter in _ADAPTERS.values()}))
        raise KeyError(f"unknown adapter {name!r}; available adapters: {available}")
    return _ADAPTERS[key]


def iter_adapters() -> list[BaseAdapter]:
    seen: set[str] = set()
    adapters: list[BaseAdapter] = []
    for adapter in _ADAPTERS.values():
        if adapter.name not in seen:
            adapters.append(adapter)
            seen.add(adapter.name)
    return adapters
