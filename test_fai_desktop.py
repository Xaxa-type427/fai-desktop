"""Offline contract tests for the FAI VPS adapter; no real network access."""
import io
import json
import unittest
from unittest.mock import patch
import fai_desktop


class TestVPSAdapter(unittest.TestCase):
    def test_requires_https_and_model(self):
        with patch.object(fai_desktop, "BASE_URL", "http://localhost:8000/v1"), patch.object(fai_desktop, "MODEL", "qwen"):
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                fai_desktop.ask([{"role": "user", "content": "hello"}])

    def test_valid_request_and_response(self):
        response = {"choices": [{"message": {"content": "FAI online"}}]}
        payload = io.BytesIO(json.dumps(response).encode())
        with patch.object(fai_desktop, "BASE_URL", "https://example.invalid/v1"), \
             patch.object(fai_desktop, "MODEL", "qwen"), \
             patch.object(fai_desktop, "TOKEN", "test-token"), \
             patch.object(fai_desktop.request, "urlopen", return_value=payload) as mocked:
            answer = fai_desktop.ask([{"role": "user", "content": "hello"}])
        self.assertEqual(answer, "FAI online")
        req = mocked.call_args.args[0]
        self.assertEqual(req.full_url, "https://example.invalid/v1/chat/completions")
        self.assertEqual(req.get_header("Authorization"), "Bearer test-token")
        body = json.loads(req.data)
        self.assertEqual(body["model"], "qwen")
        self.assertEqual(body["messages"][0]["content"], "hello")

    def test_invalid_api_response_fails(self):
        with patch.object(fai_desktop, "BASE_URL", "https://example.invalid/v1"), \
             patch.object(fai_desktop, "MODEL", "qwen"), \
             patch.object(fai_desktop.request, "urlopen", return_value=io.BytesIO(b'{"choices": []}')):
            with self.assertRaises(IndexError):
                fai_desktop.ask([{"role": "user", "content": "hello"}])


if __name__ == "__main__":
    unittest.main()
