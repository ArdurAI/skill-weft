from __future__ import annotations

from pathlib import Path

from ..models import LaunchPlan
from .base import BaseAdapter, task_with_context


class CursorAdapter(BaseAdapter):
    name = "cursor"
    executable_names = ("agent", "cursor-agent")
    install_hint = "Install Cursor CLI with: curl https://cursor.com/install -fsS | bash"

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        prompt = task_with_context(task, context_pack)
        return LaunchPlan(
            command=("agent", "-p", prompt),
            notes=("Cursor CLI uses agent -p for headless mode; future adapter should also export .cursor/rules and .agents/skills",),
        )
