import tempfile
from pathlib import Path
import unittest

from skillhub.registry import load_skill


class RegistryTest(unittest.TestCase):
    def test_load_skill_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            p.write_text("---\nname: test-skill\ndescription: Does testing\ntags: [test, python]\n---\n# Body\n", encoding="utf-8")
            skill = load_skill(p)
            self.assertEqual(skill.name, "test-skill")
            self.assertEqual(skill.description, "Does testing")
            self.assertEqual(skill.tags, ("test", "python"))
