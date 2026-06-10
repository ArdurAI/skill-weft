from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from .maintenance import audit
from .packer import pack_json, pack_text
from .registry import iter_skills
from .router import suggest


def cmd_add(args: argparse.Namespace) -> int:
    src = Path(args.skill_file)
    dest_dir = Path(args.registry)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    print(str(dest))
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    skills = list(iter_skills(args.registry))
    suggestions = suggest(args.task, skills, limit=args.limit)
    data = [
        {"name": s.skill.name, "score": s.score, "reasons": list(s.reasons), "path": str(s.skill.path)}
        for s in suggestions
    ]
    print(json.dumps(data, indent=2))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    skills = list(iter_skills(args.registry))
    suggestions = suggest(args.task, skills, limit=args.max_skills)
    if args.format == "json":
        print(pack_json(args.task, suggestions))
    else:
        print(pack_text(args.task, suggestions))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    findings = audit(list(iter_skills(args.registry)))
    print(json.dumps([f.__dict__ for f in findings], indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillhub")
    sub = parser.add_subparsers(required=True)

    add = sub.add_parser("add", help="copy a Markdown skill into the registry")
    add.add_argument("skill_file")
    add.add_argument("--registry", default=".skillhub/skills")
    add.set_defaults(func=cmd_add)

    suggest_cmd = sub.add_parser("suggest", help="suggest relevant skills for a task")
    suggest_cmd.add_argument("task")
    suggest_cmd.add_argument("--registry", default=".skillhub/skills")
    suggest_cmd.add_argument("--limit", type=int, default=5)
    suggest_cmd.set_defaults(func=cmd_suggest)

    pack = sub.add_parser("pack", help="emit a context pack for selected skills")
    pack.add_argument("task")
    pack.add_argument("--registry", default=".skillhub/skills")
    pack.add_argument("--max-skills", type=int, default=3)
    pack.add_argument("--format", choices=["text", "json"], default="text")
    pack.set_defaults(func=cmd_pack)

    audit_cmd = sub.add_parser("audit", help="audit skills for maintenance issues")
    audit_cmd.add_argument("--registry", default=".skillhub/skills")
    audit_cmd.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
