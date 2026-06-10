from __future__ import annotations

import re
from .models import Skill, Suggestion

STOPWORDS = {
    "a", "an", "and", "are", "as", "for", "in", "is", "it", "of", "on", "or", "the", "to", "with",
    "i", "want", "need", "do", "this", "that", "tool", "ai", "agent"
}


def tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9][a-z0-9_-]+", text.lower()) if t not in STOPWORDS}


def suggest(task: str, skills: list[Skill], limit: int = 5) -> list[Suggestion]:
    task_terms = tokenize(task)
    out: list[Suggestion] = []
    for skill in skills:
        name_terms = tokenize(skill.name)
        desc_terms = tokenize(skill.description)
        tag_terms = set(t.lower() for t in skill.tags)
        content_terms = tokenize(skill.content[:4000])

        score = 0
        reasons: list[str] = []
        name_hits = task_terms & name_terms
        desc_hits = task_terms & desc_terms
        tag_hits = task_terms & tag_terms
        content_hits = task_terms & content_terms

        if name_hits:
            score += 5 * len(name_hits)
            reasons.append("name matched: " + ", ".join(sorted(name_hits)))
        if tag_hits:
            score += 4 * len(tag_hits)
            reasons.append("tags matched: " + ", ".join(sorted(tag_hits)))
        if desc_hits:
            score += 3 * len(desc_hits)
            reasons.append("description matched: " + ", ".join(sorted(desc_hits)))
        if content_hits:
            score += len(content_hits)
            reasons.append("content matched: " + ", ".join(sorted(list(content_hits))[:8]))
        if score > 0:
            matched_terms = tuple(sorted(name_hits | desc_hits | tag_hits | content_hits))
            out.append(Suggestion(skill=skill, score=score, reasons=tuple(reasons), matched_terms=matched_terms))
    return sorted(out, key=lambda s: (-s.score, s.skill.name))[:limit]
