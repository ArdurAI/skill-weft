from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from ..models import AdapterStatus, LaunchPlan


class BaseAdapter:
    """Base class for side-effect-free AI tool launch adapters."""

    name = "base"
    executable_names: tuple[str, ...] = ()
    install_hint: str | None = None

    def find_executable(self) -> str | None:
        for executable in self.executable_names:
            path = shutil.which(executable)
            if path:
                return path
        return None

    def version_command(self, executable: str) -> list[str]:
        return [executable, "--version"]

    def detect_version(self, executable: str) -> str | None:
        try:
            completed = subprocess.run(
                self.version_command(executable),
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=5,
            )
        except Exception:
            return None
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        return lines[0] if lines else None

    def integration_status(self) -> AdapterStatus:
        executable = self.find_executable()
        if not executable:
            return AdapterStatus(
                name=self.name,
                available=False,
                install_hint=self.install_hint,
                details=("executable not found on PATH",),
            )
        return AdapterStatus(
            name=self.name,
            available=True,
            executable=executable,
            version=self.detect_version(executable),
            details=("preflight dry-run supported",),
            install_hint=self.install_hint,
        )

    def build_launch_plan(self, task: str, context_pack: str, workdir: Path | None = None, **kwargs: object) -> LaunchPlan:
        raise NotImplementedError


def task_with_context(task: str, context_pack: str) -> str:
    return f"{context_pack.rstrip()}\n\nUser task: {task}\n"
