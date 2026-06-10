from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    tags: tuple[str, ...]
    content: str
    path: Path


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
    return Skill(name=name, description=description, tags=tags, content=body.strip(), path=p)


def iter_skills(registry: str | Path) -> Iterable[Skill]:
    root = Path(registry)
    if not root.exists():
        return []
    paths = sorted(root.rglob("*.md"))
    return [load_skill(p) for p in paths]
