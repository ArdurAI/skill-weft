from __future__ import annotations

from dataclasses import dataclass
from .registry import Skill


@dataclass(frozen=True)
class AuditFinding:
    skill_name: str
    severity: str
    message: str


def audit_skill(skill: Skill) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    if not skill.description:
        findings.append(AuditFinding(skill.name, "warning", "missing description metadata"))
    if not skill.tags:
        findings.append(AuditFinding(skill.name, "info", "missing tags metadata"))
    lower = skill.content.lower()
    if "verification" not in lower and "verify" not in lower:
        findings.append(AuditFinding(skill.name, "warning", "missing verification guidance"))
    if "example" not in lower and "```" not in skill.content:
        findings.append(AuditFinding(skill.name, "info", "missing examples or code blocks"))
    if len(skill.content.split()) < 80:
        findings.append(AuditFinding(skill.name, "info", "skill content is very short"))
    return findings


def audit(skills: list[Skill]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for skill in skills:
        findings.extend(audit_skill(skill))
    return findings
