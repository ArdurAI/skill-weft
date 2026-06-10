import unittest
from pathlib import Path

from skillweft.models import AdapterStatus, ContextPack, LaunchPlan, Skill, Suggestion


class ModelsTest(unittest.TestCase):
    def test_skill_keeps_backwards_compatible_constructor_and_exposes_id(self):
        skill = Skill("python-debugging", "Debug Python", ("python",), "body", Path("skills/python.md"))

        self.assertEqual(skill.name, "python-debugging")
        self.assertEqual(skill.id, "python-debugging")
        self.assertEqual(skill.trust_level, "unknown")

    def test_context_pack_and_launch_plan_are_json_ready(self):
        skill = Skill("python-debugging", "Debug Python", ("python",), "body", Path("skills/python.md"))
        suggestion = Suggestion(skill=skill, score=10, reasons=("tags matched: python",), matched_terms=("python",))
        pack = ContextPack(
            task="debug pytest",
            target="codex",
            skills=(suggestion,),
            content="packed context",
            estimated_tokens=3,
            budget=100,
            truncated=False,
        )
        plan = LaunchPlan(
            command=("codex", "exec", "-"),
            stdin="packed context",
            env={"A": "B"},
            temp_files={"context.md": "packed context"},
            notes=("dry-run",),
        )
        status = AdapterStatus(name="codex", available=True, executable="/usr/bin/codex", version="1.0")

        self.assertEqual(pack.skills[0].skill.id, "python-debugging")
        self.assertEqual(plan.as_dict()["command"], ["codex", "exec", "-"])
        self.assertEqual(status.as_dict()["available"], True)


if __name__ == "__main__":
    unittest.main()
