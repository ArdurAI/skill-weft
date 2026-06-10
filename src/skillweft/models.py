from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class Skill:
    """A portable skill loaded from a SkillWeft registry."""

    name: str
    description: str
    tags: tuple[str, ...]
    content: str
    path: Path
    version: str | None = None
    source: str | None = None
    trust_level: str = "unknown"
    skill_id: str | None = None

    @property
    def id(self) -> str:
        return self.skill_id or self.name

    def as_dict(self, include_content: bool = True) -> dict[str, object]:
        data: dict[str, object] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "path": str(self.path),
            "version": self.version,
            "source": self.source,
            "trust_level": self.trust_level,
        }
        if include_content:
            data["content"] = self.content
        return data


@dataclass(frozen=True)
class Suggestion:
    """A routed skill recommendation with explainable scoring metadata."""

    skill: Skill
    score: float
    reasons: tuple[str, ...]
    matched_terms: tuple[str, ...] = ()

    def as_dict(self, include_content: bool = False) -> dict[str, object]:
        return {
            "skill": self.skill.as_dict(include_content=include_content),
            "name": self.skill.name,
            "score": self.score,
            "reasons": list(self.reasons),
            "matched_terms": list(self.matched_terms),
            "path": str(self.skill.path),
        }


@dataclass(frozen=True)
class ContextPack:
    """Packed context for a specific task and target adapter."""

    task: str
    target: str
    skills: tuple[Suggestion, ...]
    content: str
    estimated_tokens: int
    budget: int | None = None
    truncated: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "task": self.task,
            "target": self.target,
            "skills": [s.as_dict(include_content=False) for s in self.skills],
            "content": self.content,
            "estimated_tokens": self.estimated_tokens,
            "budget": self.budget,
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class LaunchPlan:
    """A side-effect-free description of how SkillWeft would launch an agent."""

    command: tuple[str, ...]
    stdin: str | None = None
    env: Mapping[str, str] = field(default_factory=dict)
    temp_files: Mapping[str, str] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def as_dict(self, include_full_payloads: bool = True) -> dict[str, object]:
        data: dict[str, object] = {
            "command": list(self.command),
            "env": dict(self.env),
            "temp_files": dict(self.temp_files),
            "notes": list(self.notes),
        }
        if include_full_payloads:
            data["stdin"] = self.stdin
        else:
            data["stdin_preview"] = (self.stdin[:500] + "…") if self.stdin and len(self.stdin) > 500 else self.stdin
            data["temp_files"] = {k: ((v[:500] + "…") if len(v) > 500 else v) for k, v in self.temp_files.items()}
        return data


@dataclass(frozen=True)
class AdapterStatus:
    """Detected integration status for an AI tool adapter."""

    name: str
    available: bool
    executable: str | None = None
    version: str | None = None
    details: tuple[str, ...] = ()
    install_hint: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "available": self.available,
            "executable": self.executable,
            "version": self.version,
            "details": list(self.details),
            "install_hint": self.install_hint,
        }
