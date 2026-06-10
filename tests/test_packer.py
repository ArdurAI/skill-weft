import unittest
from pathlib import Path

from skillhub.packer import pack_text
from skillhub.registry import Skill
from skillhub.router import Suggestion


class PackerTest(unittest.TestCase):
    def test_pack_text_includes_reason_and_content(self):
        skill = Skill("s", "desc", ("tag",), "body", Path("s.md"))
        text = pack_text("task", [Suggestion(skill, 1, ("reason",))])
        self.assertIn("SkillHub Context Pack", text)
        self.assertIn("Why selected: reason", text)
        self.assertIn("body", text)
