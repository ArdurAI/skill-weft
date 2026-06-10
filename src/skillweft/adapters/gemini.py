from __future__ import annotations

from pathlib import Path

from ..models import LaunchPlan
from .base import BaseAdapter


class GeminiAdapter(BaseAdapter):
    name = "gemini"
    executable_names = ("gemini",)
    install_hint = "Install Gemini CLI with: npm install -g @google/gemini-cli"

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        return LaunchPlan(
            command=("gemini", "-p", task, "--output-format", "json"),
            stdin=context_pack,
            notes=("Gemini headless mode accepts -p/--prompt and appends stdin, keeping large context out of shell arguments",),
        )
