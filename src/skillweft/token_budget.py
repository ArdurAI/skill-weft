from __future__ import annotations

import math


TRUNCATION_MARKER = "\n\n[truncated by SkillWeft to fit context budget]\n"


def estimate_tokens(text: str) -> int:
    """Cheap deterministic token estimate: roughly four characters per token."""

    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def truncate_to_token_budget(text: str, budget: int | None) -> tuple[str, bool]:
    """Return text that fits a rough token budget plus a truncation flag.

    The budget is intentionally approximate because SkillWeft should not depend on
    a model-specific tokenizer in the core MVP. Callers can replace this later
    with adapter-specific tokenizers.
    """

    if budget is None or budget <= 0:
        return text, False
    if estimate_tokens(text) <= budget:
        return text, False

    max_chars = max(0, budget * 4 - len(TRUNCATION_MARKER))
    if max_chars <= 0:
        return TRUNCATION_MARKER.strip() + "\n", True
    return text[:max_chars].rstrip() + TRUNCATION_MARKER, True
