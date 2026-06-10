import unittest
from pathlib import Path

from skillhub.maintenance import audit_skill
from skillhub.registry import Skill


class MaintenanceTest(unittest.TestCase):
    def test_audit_flags_missing_description(self):
        findings = audit_skill(Skill("tiny", "", tuple(), "short", Path("tiny.md")))
        messages = [f.message for f in findings]
        self.assertIn("missing description metadata", messages)
