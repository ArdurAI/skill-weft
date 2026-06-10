import unittest
from pathlib import Path

from skillhub.registry import Skill
from skillhub.router import suggest


class RouterTest(unittest.TestCase):
    def test_suggest_matches_tags_and_description(self):
        skills = [
            Skill("python-debugging", "Debug Python tests", ("python", "pytest"), "traceback failure", Path("a.md")),
            Skill("design", "Create visuals", ("diagram",), "colors layout", Path("b.md")),
        ]
        results = suggest("fix failing pytest traceback", skills, limit=1)
        self.assertEqual(results[0].skill.name, "python-debugging")
        self.assertGreater(results[0].score, 0)
