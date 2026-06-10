import contextlib
import io
import json
import tempfile
from pathlib import Path
import unittest

from skillweft.cli import main


class CliPhaseOneTest(unittest.TestCase):
    def test_doctor_json_lists_core_adapters(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["doctor", "--format", "json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        names = {item["name"] for item in payload["adapters"]}
        self.assertGreaterEqual({"claude", "codex", "gemini", "hermes", "cursor"}, names)

    def test_run_dry_run_json_builds_context_pack_and_launch_plan(self):
        with tempfile.TemporaryDirectory() as d:
            registry = Path(d) / "skills"
            registry.mkdir()
            (registry / "python-debugging.md").write_text(
                "---\nname: python-debugging\ndescription: Debug Python tests\ntags: [python, pytest]\n---\n"
                "# Python Debugging\n\nUse when debugging failing pytest tracebacks.\n\n## Verification\nRun tests.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([
                    "run",
                    "codex",
                    "debug failing pytest traceback",
                    "--registry",
                    str(registry),
                    "--dry-run",
                    "--format",
                    "json",
                ])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["target"], "codex")
        self.assertEqual(payload["launch_plan"]["command"][:3], ["codex", "exec", "-"])
        self.assertEqual(payload["selected_skills"][0]["name"], "python-debugging")
        self.assertIn("SkillWeft Context Pack", payload["context_pack"])


if __name__ == "__main__":
    unittest.main()
