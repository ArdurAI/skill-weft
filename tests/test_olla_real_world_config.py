import os
import unittest

from skillweft.realworld.olla import OllaConfig, build_chat_completion_payload, extract_message_text


class OllaRealWorldConfigTest(unittest.TestCase):
    def test_config_reads_env_and_normalizes_base_url(self):
        env = {
            "OLLA_API_KEY": "test-key",
            "OLLA_BASE_URL": "https://example.test/v1/",
            "OLLA_MODEL": "olla-test-model",
        }

        config = OllaConfig.from_env(env)

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.base_url, "https://example.test/v1")
        self.assertEqual(config.model, "olla-test-model")
        self.assertEqual(config.chat_completions_url, "https://example.test/v1/chat/completions")

    def test_config_missing_key_is_not_ready_without_leaking_secret(self):
        config = OllaConfig.from_env({})

        self.assertFalse(config.ready)
        self.assertIn("OLLA_API_KEY", config.missing_reason)
        self.assertNotIn("Bearer", config.safe_summary())

    def test_payload_is_openai_compatible_and_deterministic(self):
        payload = build_chat_completion_payload(
            model="olla-test-model",
            system="system prompt",
            user="user prompt",
            temperature=0,
        )

        self.assertEqual(payload["model"], "olla-test-model")
        self.assertEqual(payload["temperature"], 0)
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["messages"][0], {"role": "system", "content": "system prompt"})
        self.assertEqual(payload["messages"][1], {"role": "user", "content": "user prompt"})

    def test_extract_message_text_accepts_common_chat_completion_shapes(self):
        payload = {"choices": [{"message": {"content": "{\"relevant\": true}"}}]}

        self.assertEqual(extract_message_text(payload), '{"relevant": true}')


if __name__ == "__main__":
    unittest.main()
