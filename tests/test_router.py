import unittest
from pathlib import Path

from skillweft.registry import Skill
from skillweft.router import suggest


class RouterTest(unittest.TestCase):
    def test_suggest_matches_tags_and_description(self):
        skills = [
            Skill("python-debugging", "Debug Python tests", ("python", "pytest"), "traceback failure", Path("a.md")),
            Skill("design", "Create visuals", ("diagram",), "colors layout", Path("b.md")),
        ]
        results = suggest("fix failing pytest traceback", skills, limit=1)
        self.assertEqual(results[0].skill.name, "python-debugging")
        self.assertGreater(results[0].score, 0)

    def test_generic_cli_terms_do_not_overpower_specific_domain_terms(self):
        skills = [
            Skill("native-mcp", "Model Context Protocol integration", ("mcp",), "mcp tools resources prompts", Path("mcp.md")),
            Skill("email-cli", "CLI email server", ("cli",), "configure server cli commands", Path("email.md")),
        ]
        results = suggest("configure mcp server from cli", skills, limit=1)
        self.assertEqual(results[0].skill.name, "native-mcp")

    def test_generic_create_push_terms_do_not_select_unrelated_push_workflow(self):
        skills = [
            Skill("github-workflows", "GitHub repository workflow", ("github", "repositories"), "github repository", Path("github.md")),
            Skill("webhook-subscriptions", "Event webhook automation", ("push",), "create github push events", Path("webhook.md")),
        ]
        results = suggest("create a public GitHub repository and push local code", skills, limit=3)
        self.assertEqual([result.skill.name for result in results], ["github-workflows"])
