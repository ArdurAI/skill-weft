from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from .adapters import get_adapter, iter_adapters
from .maintenance import audit
from .packer import pack_json, pack_text
from .models import LaunchPlan, Suggestion
from .registry import iter_skills
from .router import suggest
from .token_budget import estimate_tokens


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
        print(pack_json(args.task, suggestions, budget=args.budget, target=args.target))
    else:
        print(pack_text(args.task, suggestions, budget=args.budget, target=args.target))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    findings = audit(list(iter_skills(args.registry)))
    print(json.dumps([f.__dict__ for f in findings], indent=2))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    statuses = [adapter.integration_status() for adapter in iter_adapters()]
    payload = {"adapters": [status.as_dict() for status in statuses]}
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print("SkillWeft doctor")
        for status in statuses:
            mark = "✓" if status.available else "✗"
            version = f" ({status.version})" if status.version else ""
            executable = f" at {status.executable}" if status.executable else ""
            print(f"{mark} {status.name}{version}{executable}")
            if not status.available and status.install_hint:
                print(f"  install: {status.install_hint}")
    return 0


def _build_context_and_plan(args: argparse.Namespace) -> tuple[list[Suggestion], str, LaunchPlan]:
    skills = list(iter_skills(args.registry))
    suggestions = suggest(args.task, skills, limit=args.max_skills)
    context_pack = pack_text(args.task, suggestions, budget=args.budget, target=args.target)
    adapter = get_adapter(args.target)
    plan = adapter.build_launch_plan(args.task, context_pack, workdir=Path(args.workdir) if args.workdir else Path.cwd())
    return suggestions, context_pack, plan


def cmd_run(args: argparse.Namespace) -> int:
    suggestions, context_pack, plan = _build_context_and_plan(args)
    payload = {
        "target": args.target,
        "task": args.task,
        "selected_skills": [s.as_dict(include_content=False) for s in suggestions],
        "context_estimated_tokens": estimate_tokens(context_pack),
        "context_pack": context_pack,
        "launch_plan": plan.as_dict(include_full_payloads=args.format == "json"),
    }
    if args.dry_run:
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(f"SkillWeft dry run for {args.target}")
            print("Selected skills:")
            for suggestion in suggestions:
                print(f"- {suggestion.skill.name} (score={suggestion.score}): {'; '.join(suggestion.reasons)}")
            print("\nCommand:")
            print(" ".join(plan.command))
            if plan.stdin:
                print("\nStdin preview:")
                print(plan.stdin[:1000])
            if plan.temp_files:
                print("\nTemp files:")
                for name in plan.temp_files:
                    print(f"- {name}")
        return 0

    with tempfile.TemporaryDirectory(prefix="skillweft-") as temp_dir:
        command = list(plan.command)
        for file_name, content in plan.temp_files.items():
            path = Path(temp_dir) / file_name
            path.write_text(content, encoding="utf-8")
            command = [str(path) if part == file_name else part for part in command]
        completed = subprocess.run(
            command,
            input=plan.stdin,
            text=True,
            env={**os.environ, **dict(plan.env)} if plan.env else None,
            cwd=args.workdir or None,
            check=False,
        )
        return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillweft")
    sub = parser.add_subparsers(required=True)

    add = sub.add_parser("add", help="copy a Markdown skill into the registry")
    add.add_argument("skill_file")
    add.add_argument("--registry", default=".skillweft/skills")
    add.set_defaults(func=cmd_add)

    suggest_cmd = sub.add_parser("suggest", help="suggest relevant skills for a task")
    suggest_cmd.add_argument("task")
    suggest_cmd.add_argument("--registry", default=".skillweft/skills")
    suggest_cmd.add_argument("--limit", type=int, default=5)
    suggest_cmd.set_defaults(func=cmd_suggest)

    pack = sub.add_parser("pack", help="emit a context pack for selected skills")
    pack.add_argument("task")
    pack.add_argument("--registry", default=".skillweft/skills")
    pack.add_argument("--max-skills", type=int, default=3)
    pack.add_argument("--budget", type=int, default=None, help="approximate token budget for the context pack")
    pack.add_argument("--target", default="generic", help="target adapter name for context-pack metadata")
    pack.add_argument("--format", choices=["text", "json"], default="text")
    pack.set_defaults(func=cmd_pack)

    run = sub.add_parser("run", help="route a task, pack selected skills, and build or execute an agent launch plan")
    run.add_argument("target", help="target adapter: claude, codex, gemini, hermes, cursor")
    run.add_argument("task")
    run.add_argument("--registry", default=".skillweft/skills")
    run.add_argument("--max-skills", type=int, default=3)
    run.add_argument("--budget", type=int, default=6000)
    run.add_argument("--workdir", default=None)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--format", choices=["text", "json"], default="text")
    run.set_defaults(func=cmd_run)

    doctor = sub.add_parser("doctor", help="check which AI tool adapters are available")
    doctor.add_argument("--format", choices=["text", "json"], default="text")
    doctor.set_defaults(func=cmd_doctor)

    audit_cmd = sub.add_parser("audit", help="audit skills for maintenance issues")
    audit_cmd.add_argument("--registry", default=".skillweft/skills")
    audit_cmd.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
