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

    def is_hidden_descendant(path: Path) -> bool:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        return any(part.startswith(".") for part in rel.parts)

    all_paths = [
        p
        for p in sorted(root.rglob("*.md"))
        if not is_hidden_descendant(p) and p.name != "DESCRIPTION.md"
    ]
    package_dirs = {p.parent for p in all_paths if p.name == "SKILL.md"}

    def is_inside_package_support_file(path: Path) -> bool:
        if path.name == "SKILL.md":
            return False
        return any(package_dir in path.parents for package_dir in package_dirs)

    paths = [p for p in all_paths if not is_inside_package_support_file(p)]
    return [load_skill(p) for p in paths]
