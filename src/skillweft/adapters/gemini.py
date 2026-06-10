from __future__ import annotations

from pathlib import Path

from ..models import LaunchPlan
from .base import BaseAdapter, task_with_context


class GeminiAdapter(BaseAdapter):
    name = "gemini"
    executable_names = ("gemini",)
    install_hint = "Install Gemini CLI with: npm install -g @google/gemini-cli"

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        prompt = task_with_context(task, context_pack)
        return LaunchPlan(
            command=("gemini", "-p", prompt, "--output-format", "json"),
            notes=("Gemini headless mode accepts -p/--prompt",),
        )
