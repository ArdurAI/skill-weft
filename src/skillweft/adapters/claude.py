from __future__ import annotations

from pathlib import Path

from ..models import LaunchPlan
from .base import BaseAdapter, task_with_context


class ClaudeAdapter(BaseAdapter):
    name = "claude"
    executable_names = ("claude",)
    install_hint = "Install Claude Code with: npm install -g @anthropic-ai/claude-code"

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        max_turns = str(kwargs.get("max_turns", 10))
        context_file = "skillweft-context.md"
        return LaunchPlan(
            command=("claude", "-p", task, "--append-system-prompt-file", context_file, "--max-turns", max_turns),
            temp_files={context_file: context_pack},
            notes=("create temp context file before execution", "print mode skips interactive workspace dialogs"),
        )
