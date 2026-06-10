import unittest
from pathlib import Path

from skillweft.packer import pack_text
from skillweft.registry import Skill
from skillweft.router import Suggestion


class PackerTest(unittest.TestCase):
    def test_pack_text_includes_reason_and_content(self):
        skill = Skill("s", "desc", ("tag",), "body", Path("s.md"))
        text = pack_text("task", [Suggestion(skill, 1, ("reason",))])
        self.assertIn("SkillWeft Context Pack", text)
        self.assertIn("Why selected: reason", text)
        self.assertIn("body", text)

    def test_pack_text_respects_budget(self):
        skill = Skill("large", "desc", ("tag",), "word " * 1000, Path("large.md"))
        text = pack_text("task", [Suggestion(skill, 1, ("reason",))], budget=120)
        self.assertIn("SkillWeft Context Pack", text)
        self.assertIn("[truncated by SkillWeft", text)
        self.assertNotIn("word " * 1000, text)
