from __future__ import annotations

from pathlib import Path

from ..models import LaunchPlan
from .base import BaseAdapter, task_with_context


class CodexAdapter(BaseAdapter):
    name = "codex"
    executable_names = ("codex",)
    install_hint = "Install Codex CLI with: npm install -g @openai/codex"

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        root = str(workdir or Path.cwd())
        sandbox = str(kwargs.get("sandbox", "workspace-write"))
        return LaunchPlan(
            command=("codex", "exec", "-", "--cd", root, "--sandbox", sandbox),
            stdin=task_with_context(task, context_pack),
            notes=("instructions are read from stdin via codex exec -",),
        )
