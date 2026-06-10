from __future__ import annotations

from pathlib import Path

from ..models import LaunchPlan
from .base import BaseAdapter, task_with_context


class HermesAdapter(BaseAdapter):
    name = "hermes"
    executable_names = ("hermes",)
    install_hint = "Install Hermes Agent from https://hermes-agent.nousresearch.com/docs"

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        prompt = task_with_context(task, context_pack)
        return LaunchPlan(
            command=("hermes", "chat", "-q", prompt),
            notes=("Hermes can also be integrated later through native skills and MCP",),
        )
