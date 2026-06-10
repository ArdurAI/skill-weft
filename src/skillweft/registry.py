from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

from .models import Skill


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip('"')
    return meta, body


def _parse_tags(value: str) -> tuple[str, ...]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return tuple(t.strip().strip('"\'') for t in value.split(",") if t.strip())


def load_skill(path: str | Path) -> Skill:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    name = meta.get("name") or (heading.group(1) if heading else p.stem)
    description = meta.get("description") or ""
    tags = _parse_tags(meta.get("tags", ""))
    return Skill(
        name=name,
        description=description,
        tags=tags,
        content=body.strip(),
        path=p,
        version=meta.get("version"),
        source=meta.get("source"),
        trust_level=meta.get("trust_level", meta.get("trust-level", "unknown")),
        skill_id=meta.get("id"),
    )


def iter_skills(registry: str | Path) -> Iterable[Skill]:
    root = Path(registry)
    if not root.exists():
        return []
    paths = sorted(root.rglob("*.md"))
    return [load_skill(p) for p in paths]
