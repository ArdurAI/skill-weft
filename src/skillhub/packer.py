from __future__ import annotations

import json
from .router import Suggestion


def pack_text(task: str, suggestions: list[Suggestion]) -> str:
    blocks = [f"# SkillHub Context Pack\n\nTask: {task}\n"]
    for item in suggestions:
        skill = item.skill
        blocks.append(
            "\n---\n"
            f"## Skill: {skill.name}\n"
            f"Description: {skill.description}\n"
            f"Tags: {', '.join(skill.tags)}\n"
            f"Why selected: {'; '.join(item.reasons)}\n\n"
            f"{skill.content}\n"
        )
    return "".join(blocks).strip() + "\n"


def pack_json(task: str, suggestions: list[Suggestion]) -> str:
    payload = {
        "task": task,
        "skills": [
            {
                "name": s.skill.name,
                "description": s.skill.description,
                "tags": list(s.skill.tags),
                "path": str(s.skill.path),
                "score": s.score,
                "reasons": list(s.reasons),
                "content": s.skill.content,
            }
            for s in suggestions
        ],
    }
    return json.dumps(payload, indent=2)
