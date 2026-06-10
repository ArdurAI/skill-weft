import unittest
from pathlib import Path

from skillweft.adapters import get_adapter, iter_adapters


class AdapterTest(unittest.TestCase):
    def test_known_adapters_are_registered(self):
        names = {adapter.name for adapter in iter_adapters()}

        self.assertGreaterEqual({"claude", "codex", "gemini", "hermes", "cursor"}, names)

    def test_codex_adapter_builds_stdin_preflight_plan(self):
        adapter = get_adapter("codex")
        plan = adapter.build_launch_plan("debug pytest", "# SkillWeft Context Pack", workdir=Path("/tmp/project"))

        self.assertEqual(plan.command[:3], ("codex", "exec", "-"))
        self.assertIn("--cd", plan.command)
        self.assertIn("/tmp/project", plan.command)
        self.assertIn("# SkillWeft Context Pack", plan.stdin or "")
        self.assertIn("User task: debug pytest", plan.stdin or "")

    def test_claude_adapter_uses_context_temp_file(self):
        adapter = get_adapter("claude")
        plan = adapter.build_launch_plan("debug pytest", "# SkillWeft Context Pack")

        self.assertEqual(plan.command[0], "claude")
        self.assertIn("--append-system-prompt-file", plan.command)
        self.assertIn("skillweft-context.md", plan.temp_files)
        self.assertIn("# SkillWeft Context Pack", plan.temp_files["skillweft-context.md"])

    def test_adapter_status_is_json_ready_even_when_tool_missing(self):
        status = get_adapter("cursor").integration_status()

        self.assertEqual(status.name, "cursor")
        self.assertIn("available", status.as_dict())


if __name__ == "__main__":
    unittest.main()
