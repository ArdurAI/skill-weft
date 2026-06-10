import json
import os
from pathlib import Path
import unittest

from skillweft.packer import pack_text
from skillweft.realworld.olla import OllaConfig, call_olla_chat, parse_json_object
from skillweft.registry import iter_skills
from skillweft.router import suggest


RUN_REAL_WORLD = os.environ.get("SKILLWEFT_RUN_OLLA_REAL_WORLD") == "1"
CONFIG = OllaConfig.from_env(os.environ)


@unittest.skipUnless(RUN_REAL_WORLD, "set SKILLWEFT_RUN_OLLA_REAL_WORLD=1 to allow paid/network Olla tests")
@unittest.skipUnless(CONFIG.ready, "set OLLA_API_KEY to run Olla real-world tests")
class OllaAPIRealWorldTest(unittest.TestCase):
    maxDiff = 2000

    def setUp(self):
        registry = Path(os.environ.get("SKILLWEFT_REAL_REGISTRY", "~/.hermes/skills")).expanduser()
        self.skills = list(iter_skills(registry))
        if not self.skills:
            self.skipTest(f"no skills found in {registry}")

    def judge_pack(self, *, task, expected_any, max_skills=2):
        suggestions = suggest(task, self.skills, limit=max_skills)
        selected_names = [s.skill.name for s in suggestions]
        self.assertTrue(
            any(name in selected_names for name in expected_any),
            f"expected one of {expected_any}, got {selected_names}",
        )
        context_pack = pack_text(task, suggestions, target="olla-real-world", budget=1800)
        system = (
            "You are a strict QA judge for SkillWeft, an AI skill router. "
            "Decide whether the selected skills are directly useful for the user task. "
            "Return JSON only with keys: relevant (boolean), unrelated_skills (array of strings), "
            "missing_expected_skills (array of strings), reason (string). "
            "Mark relevant=false if the pack contains unrelated skills or misses the expected workflow."
        )
        user = json.dumps(
            {
                "task": task,
                "expected_any_skill": list(expected_any),
                "selected_skill_names": selected_names,
                "context_pack": context_pack,
            },
            indent=2,
        )
        response_text = call_olla_chat(CONFIG, system=system, user=user)
        verdict = parse_json_object(response_text)
        self.assertIs(verdict.get("relevant"), True, verdict)
        self.assertEqual(verdict.get("unrelated_skills", []), [], verdict)
        return {"selected_names": selected_names, "verdict": verdict}

    def test_olla_judges_github_repo_task_pack_relevant(self):
        result = self.judge_pack(
            task="create a public GitHub repository and push local code",
            expected_any=("github-workflows",),
            max_skills=2,
        )
        self.assertIn("github-workflows", result["selected_names"])

    def test_olla_judges_mcp_configuration_task_pack_relevant(self):
        result = self.judge_pack(
            task="configure an MCP server for Claude Code and Gemini CLI",
            expected_any=("native-mcp", "ai-skill-management-systems"),
            max_skills=2,
        )
        self.assertTrue({"native-mcp", "ai-skill-management-systems"} & set(result["selected_names"]))

    def test_olla_judges_planning_task_pack_relevant(self):
        result = self.judge_pack(
            task="write an implementation plan for adapter integration",
            expected_any=("writing-plans", "plan"),
            max_skills=2,
        )
        self.assertTrue({"writing-plans", "plan"} & set(result["selected_names"]))


if __name__ == "__main__":
    unittest.main()
