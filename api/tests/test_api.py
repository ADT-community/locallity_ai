import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from fastapi.testclient import TestClient

    from api import llm
    from api.main import app

    client = TestClient(app)
except ImportError:
    client = None


@unittest.skipIf(client is None, "FastAPI/httpx are not installed (see api/requirements.txt)")
class APITests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("api.service.llm_module.call_llm", return_value="Short answer.")
        self.mocked = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_chat_contract(self):
        response = client.post("/chat", json={
            "lang": "en-NG",
            "messages": [{"role": "user", "content": "How do I plant maize?"}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"reply": "Short answer.", "sources": []})

    def test_safety_deferral_needs_no_llm(self):
        response = client.post("/chat", json={
            "lang": "en-NG",
            "messages": [{"role": "user", "content": "I have a fever, what medicine should I take?"}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("local health professional", response.json()["reply"].lower())
        self.mocked.assert_not_called()

    def test_missing_key_returns_503(self):
        self.mocked.side_effect = llm.LLMError("No LLM API key configured.")
        response = client.post("/chat", json={
            "lang": "en-NG",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
        })
        self.assertEqual(response.status_code, 503)

    def test_invalid_payload_returns_422(self):
        response = client.post("/chat", json={"lang": "en-NG", "messages": []})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
