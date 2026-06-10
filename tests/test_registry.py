import tempfile
from pathlib import Path
import unittest

from skillweft.registry import iter_skills, load_skill


class RegistryTest(unittest.TestCase):
    def test_load_skill_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            p.write_text("---\nname: test-skill\ndescription: Does testing\ntags: [test, python]\n---\n# Body\n", encoding="utf-8")
            skill = load_skill(p)
            self.assertEqual(skill.name, "test-skill")
            self.assertEqual(skill.description, "Does testing")
            self.assertEqual(skill.tags, ("test", "python"))

    def test_iter_skills_prefers_skill_packages_and_skips_support_and_hidden_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            package = root / "debugging" / "python-debugging"
            (package / "references").mkdir(parents=True)
            (package / "SKILL.md").write_text(
                "---\nname: python-debugging\ndescription: Debug Python\ntags: [python]\n---\n# Python Debugging\n",
                encoding="utf-8",
            )
            (package / "references" / "details.md").write_text("# Reference Only\n", encoding="utf-8")
            (root / "loose-skill.md").write_text(
                "---\nname: loose-skill\ndescription: Loose\n---\n# Loose\n",
                encoding="utf-8",
            )
            (root / "DESCRIPTION.md").write_text("# Category description\n", encoding="utf-8")
            hidden = root / ".archive" / "old-skill"
            hidden.mkdir(parents=True)
            (hidden / "SKILL.md").write_text(
                "---\nname: archived\ndescription: Archived\n---\n# Archived\n",
                encoding="utf-8",
            )

            skills = list(iter_skills(root))

        names = [skill.name for skill in skills]
        self.assertEqual(names, ["python-debugging", "loose-skill"])
