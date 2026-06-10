import unittest

from skillweft.token_budget import estimate_tokens, truncate_to_token_budget


class TokenBudgetTest(unittest.TestCase):
    def test_estimate_tokens_uses_character_heuristic_with_minimum(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("abcd"), 1)
        self.assertEqual(estimate_tokens("abcde"), 2)

    def test_truncate_to_token_budget_preserves_marker_and_budget(self):
        text = "0123456789" * 100
        truncated, was_truncated = truncate_to_token_budget(text, budget=30)

        self.assertTrue(was_truncated)
        self.assertIn("[truncated by SkillWeft", truncated)
        self.assertLessEqual(estimate_tokens(truncated), 33)  # 10% tolerance

    def test_truncate_to_token_budget_leaves_small_text_unchanged(self):
        text = "short text"
        truncated, was_truncated = truncate_to_token_budget(text, budget=100)

        self.assertEqual(truncated, text)
        self.assertFalse(was_truncated)


if __name__ == "__main__":
    unittest.main()
