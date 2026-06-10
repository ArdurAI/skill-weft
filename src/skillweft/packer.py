from __future__ import annotations

import json
from .models import Suggestion
from .token_budget import estimate_tokens, truncate_to_token_budget


def pack_text(task: str, suggestions: list[Suggestion], budget: int | None = None, target: str = "generic") -> str:
    blocks = [
        "# SkillWeft Context Pack\n\n"
        f"Task: {task}\n"
        f"Target: {target}\n\n"
        "Use this as procedural guidance only. Load only the selected skills; do not request the full registry unless the user explicitly asks.\n"
    ]
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
    text = "".join(blocks).strip() + "\n"
    text, _ = truncate_to_token_budget(text, budget)
    return text


def pack_json(task: str, suggestions: list[Suggestion], budget: int | None = None, target: str = "generic") -> str:
    content = pack_text(task, suggestions, budget=budget, target=target)
    payload = {
        "task": task,
        "target": target,
        "budget": budget,
        "estimated_tokens": estimate_tokens(content),
        "skills": [
            {
                "id": s.skill.id,
                "name": s.skill.name,
                "description": s.skill.description,
                "tags": list(s.skill.tags),
                "path": str(s.skill.path),
                "score": s.score,
                "reasons": list(s.reasons),
                "matched_terms": list(s.matched_terms),
                "content": s.skill.content,
            }
            for s in suggestions
        ],
        "content": content,
    }
    return json.dumps(payload, indent=2)
